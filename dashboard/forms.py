from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from .models import Profile
from authentication.models import User


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User 
        fields = ['username', 'email','photo_user']
        widget = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'photo_user': forms.FileInput(attrs={'class':'form-control'}),
        }