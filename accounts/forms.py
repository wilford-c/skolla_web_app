from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password1',
            'password2',
        )


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or Email'

    def clean(self):
        """Allow guardians (and everyone else) to authenticate via email or username."""

        username_input = self.data.get(self.username_field, '')
        if username_input and '@' in username_input:
            try:
                user = User.objects.get(email__iexact=username_input)
            except User.DoesNotExist:
                pass
            else:
                mutable_data = self.data.copy()
                mutable_data[self.username_field] = user.get_username()
                self.data = mutable_data

        return super().clean()