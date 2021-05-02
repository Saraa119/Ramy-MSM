from django import forms
from django.contrib.auth.forms import UserCreationForm 
from django.utils.translation import gettext_lazy as _
from med.models import Department, Doctor, Engineer, Manager
from django_email_verification import send_email
from django.contrib.auth.forms import (PasswordResetForm, SetPasswordForm)
from .models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)


class ManagerSignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Manager
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self):
        user = super().save(commit=False)
        user.type = 'MANAGER'
        user.is_active = False
        user.save()
        send_email(user)
        return user

class EngineerSignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Engineer
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

        # department = forms.ModelChoiceField(
        #     queryset=Department.objects.all().distinct(),
        #     widget=forms.Select
        # )
    
    def save(self):
        user = super().save(commit=False)
        user.type = 'ENGINEER'
        user.is_active = False
        user.save()
        send_email(user)
        return user

class DoctorSignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = Doctor
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self):
        user = super().save(commit=False)
        user.type = 'DOCTOR'
        user.is_active = False
        user.save()
        send_email(user)
        return user


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("The email address you entered is not registered. Please enter registered email id")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_notvalid': _("Password must of 8 Character which contain alphanumeric with atleast 1 special charater and 1 uppercase."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
            # Regix to check the password must contains sepcial char, numbers, char with upeercase and lowercase.
            regex = re.compile('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%]).{8,30})')
            if(regex.search(password1) == None):
                    raise forms.ValidationError(
                    self.error_messages['password_notvalid'],
                    code='password_mismatch',
                )

        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        email = self.user.email
        instance = User.objects.get(id=self.user.id)
        if not instance.first_login:
            instance.first_login = True
            instance.save()
        return self.user