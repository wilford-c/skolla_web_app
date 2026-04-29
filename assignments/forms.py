from django import forms
from django.forms import inlineformset_factory

from .models import Assignment, AssignmentAttachment


class AssignmentForm(forms.ModelForm):
    """Form for creating and editing assignments."""
    
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'instructions', 'subject', 'classroom',
            'assigned_date', 'due_date', 'max_marks', 'status', 'allow_late_submission'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter assignment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Brief description of the assignment'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Detailed instructions for students (optional)'
            }),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'classroom': forms.Select(attrs={'class': 'form-select'}),
            'assigned_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'max_marks': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 1000
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'allow_late_submission': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        help_texts = {
            'instructions': 'Provide detailed instructions, requirements, and grading criteria.',
            'allow_late_submission': 'Allow students to submit after the due date.',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is a teacher, limit subjects and classrooms to their own
        if user and user.role == 'TEACHER':
            from academics.models import Subject, Classroom
            # Get classrooms where this teacher teaches
            teacher_classrooms = Classroom.objects.filter(
                schedules__teacher=user
            ).distinct()
            self.fields['classroom'].queryset = teacher_classrooms
            
            # Get subjects this teacher teaches
            teacher_subjects = Subject.objects.filter(
                schedules__teacher=user
            ).distinct()
            self.fields['subject'].queryset = teacher_subjects


class AssignmentAttachmentForm(forms.ModelForm):
    """Form for assignment attachments."""
    
    class Meta:
        model = AssignmentAttachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'multiple': False
            })
        }


# Formset for handling multiple attachments
AssignmentAttachmentFormSet = inlineformset_factory(
    Assignment,
    AssignmentAttachment,
    form=AssignmentAttachmentForm,
    extra=3,
    can_delete=True,
    max_num=10
)
