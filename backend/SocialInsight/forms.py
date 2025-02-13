from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    STATUS_CHOICES = (
        ('', '---- 選択してください ----'),
        ('high_schooler', '高校生'),
        ('undergrad', '大学生'),
        ('worker', '社会人'),
    )

    PART_TIME_CHOICES = (
        ('True', 'はい'),
        ('False', 'いいえ')
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='所属・職業',
        required=True
    )

    has_part_time_job = forms.ChoiceField(
        choices=PART_TIME_CHOICES,
        label='アルバイト経験はありますか？',
        widget=forms.RadioSelect(),
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            profile = Profile.objects.create(
                user=user,
                status=self.cleaned_data['status'],
                has_part_time_job=self.cleaned_data['has_part_time_job'] == 'True'
            )
            profile.save()

        return user
