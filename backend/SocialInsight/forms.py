from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    STATUS_CHOICES = (
        ('student', '学生'),
        ('worker', '社会人'),
    )

    status = forms.ChoiceField(choices=STATUS_CHOICES, label='ステータス')

    class Meta:
        model = User

        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:

            profile, created = Profile.objects.get_or_create(user=user)
            profile.status = self.cleaned_data['status']
            profile.save()

        return user