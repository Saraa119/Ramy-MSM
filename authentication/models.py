from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, reverse_lazy
from django import forms

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()     
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):

    photo_user = models.ImageField(upload_to='photos', null = True , blank = True)
    
    class Types(models.TextChoices):
        MANAGER = "MANAGER", "manager"
        ENGINEER = "ENGINEER", "engineer"
        DOCTOR = "DOCTOR", "doctor"
    photo_user = models.ImageField(upload_to='photos', null = True , blank = True)
    
    email = models.EmailField(_('email address'), unique=True)
    type = models.CharField(_("Type"), max_length= 50, choices=Types.choices, default = Types.MANAGER)
    in_hospital = models.BooleanField(_("Currently registered in a hospital"), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    