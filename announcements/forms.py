from django import forms
from django.forms import inlineformset_factory

from .models import Announcement, AnnouncementAttachment


class AnnouncementForm(forms.ModelForm):
    """Form for creating and editing announcements."""
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'priority', 'audience', 
            'target_classrooms', 'pinned', 'published', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter announcement title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 8,
                'placeholder': 'Enter announcement content'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'audience': forms.Select(attrs={'class': 'form-select'}),
            'target_classrooms': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 5
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
                'placeholder': 'YYYY-MM-DD HH:MM'
            }),
            'pinned': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        help_texts = {
            'target_classrooms': 'Hold Ctrl/Cmd to select multiple classes. Leave empty for all classes.',
            'expires_at': 'Announcement will be hidden after this date (optional).',
            'pinned': 'Pin this announcement to the top of the list.',
        }


class AnnouncementAttachmentForm(forms.ModelForm):
    """Form for announcement attachments."""
    
    class Meta:
        model = AnnouncementAttachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'multiple': False
            })
        }


# Formset for handling multiple attachments
AnnouncementAttachmentFormSet = inlineformset_factory(
    Announcement,
    AnnouncementAttachment,
    form=AnnouncementAttachmentForm,
    extra=3,
    can_delete=True,
    max_num=10
)
