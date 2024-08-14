from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext as _
from django.db import models
import logging
from django.db import connections, OperationalError
from django.core.management import call_command
from django.conf import settings
import os

from django.db import models

class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    
logger = logging.getLogger(__name__)



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        return queryset



class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = 'admin'
    STAFF = 'staff'
    STORE_MANAGER = 'store_manager'
    LOCATION_MANAGER = 'location_manager'
    MASTER_DATA_MANAGER = 'master_data_manager'
    USER_ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (STAFF, 'Staff'),
        (STORE_MANAGER, 'Store Manager'),
        (LOCATION_MANAGER, 'Location Manager'),
        (MASTER_DATA_MANAGER, 'Master Data Manager'),
    )
    name = models.CharField(_("user name"), max_length=255)
    phone = models.CharField(_("phone number"), max_length=20)
    email = models.EmailField(_("email"), max_length=255, unique=True)
    role = models.CharField(_("role"), max_length=20, choices=USER_ROLE_CHOICES)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    
    
    USERNAME_FIELD = "email"
    
    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.name
    
