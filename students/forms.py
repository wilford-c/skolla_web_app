from django import forms
from django.contrib.auth import get_user_model

from .models import Student


User = get_user_model()


class StudentForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    guardian_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label='Select linked guardian (optional)',
        help_text='Link an existing guardian account for portal access.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['guardian_user'].queryset = (
            User.objects.filter(role=User.Role.GUARDIAN)
            .order_by('first_name', 'last_name')
        )

    class Meta:
        model = Student
        fields = [
            'admission_number',
            'first_name',
            'last_name',
            'date_of_birth',
            'guardian_name',
            'guardian_user',
            'contact_email',
            'contact_phone',
            'status',
        ]
