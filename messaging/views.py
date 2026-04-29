from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from auditlog.services import log_event

from .models import Conversation, Message, MessageRead
from .realtime import broadcast_new_message


@login_required
def inbox(request):
    """Display user's conversations."""
    conversations = request.user.conversations.prefetch_related(
        'messages', 
        'messages__sender',
        'participants'
    ).order_by('-updated_at')
    
    # Add helper attributes for template
    for conversation in conversations:
        conversation.last_message = conversation.messages.last()
        conversation.other_user = conversation.get_other_participant(request.user)
        
        # Count unread messages
        unread_messages = conversation.messages.exclude(sender=request.user).exclude(
            read_receipts__user=request.user
        )
        conversation.unread_count = unread_messages.count()
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
    })


@login_required
def conversation_detail(request, pk):
    """View a conversation and send messages."""
    from .models import MessageAttachment
    from .user_status import get_user_status, get_last_seen
    
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                MessageAttachment.objects.create(
                    message=message,
                    file=file,
                    filename=file.name
                )

            # Push the new message to active websocket clients.
            broadcast_new_message(message)

            log_event(
                request=request,
                action='message.send',
                entity_type='Message',
                entity_id=str(message.pk),
                description=f'Sent message in conversation #{conversation.pk}.',
                metadata={'conversation_id': conversation.pk},
            )
            
            conversation.save()  # Update updated_at
            messages.success(request, 'Message sent!')
            return redirect('messaging:conversation', pk=conversation.pk)
    
    conversation_messages = conversation.messages.select_related('sender').prefetch_related('attachments', 'read_receipts').all()
    
    # Mark messages as read
    for msg in conversation_messages:
        if msg.sender != request.user:
            MessageRead.objects.get_or_create(message=msg, user=request.user)
    
    # Get other participant info with status
    other_participant = conversation.get_other_participant(request.user)
    if other_participant:
        other_participant.status = get_user_status(other_participant)
        other_participant.last_seen_time = get_last_seen(other_participant)
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': conversation_messages,
        'other_participant': other_participant,
    })


@login_required
def new_conversation(request):
    """Start a new conversation."""
    from django.contrib.auth import get_user_model
    from .models import MessageAttachment
    User = get_user_model()
    
    if request.method == 'POST':
        participant_ids = request.POST.getlist('participants')
        subject = request.POST.get('subject', '').strip()
        content = request.POST.get('content', '').strip()
        
        if not participant_ids:
            messages.error(request, 'Please select at least one recipient.')
            return redirect('messaging:new')
        
        if not subject:
            messages.error(request, 'Please enter a subject.')
            return redirect('messaging:new')
        
        # Create conversation
        conversation = Conversation.objects.create(subject=subject)
        
        # Add current user
        conversation.participants.add(request.user)
        
        # Add selected participants
        for participant_id in participant_ids:
            try:
                recipient = User.objects.get(id=participant_id)
                conversation.participants.add(recipient)
            except User.DoesNotExist:
                continue
        
        # Create initial message if there's content
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                MessageAttachment.objects.create(
                    message=message,
                    file=file,
                    filename=file.name
                )

        log_event(
            request=request,
            action='conversation.create',
            entity_type='Conversation',
            entity_id=str(conversation.pk),
            description=f'Created conversation "{conversation.subject}".',
            metadata={'participants_count': conversation.participants.count()},
        )
        
        messages.success(request, 'Conversation started successfully!')
        return redirect('messaging:conversation', pk=conversation.pk)
    
    # Get potential recipients based on user role
    User = get_user_model()
    
    if request.user.role == 'STUDENT':
        # Students can message teachers and admins
        available_users = User.objects.filter(role__in=['TEACHER', 'ADMIN', 'STAFF'])
    elif request.user.role == 'GUARDIAN':
        # Guardians can message teachers and admins
        available_users = User.objects.filter(role__in=['TEACHER', 'ADMIN', 'STAFF'])
    elif request.user.role == 'TEACHER':
        # Teachers can message everyone except themselves
        available_users = User.objects.filter(role__in=['STUDENT', 'GUARDIAN', 'TEACHER', 'STAFF', 'ADMIN'])
    elif request.user.role in ['ADMIN', 'STAFF']:
        # Admin/Staff can message everyone
        available_users = User.objects.all()
    else:
        available_users = User.objects.all()
    
    # Exclude current user and order by name
    available_users = available_users.exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    return render(request, 'messaging/new.html', {
        'available_users': available_users,
    })
