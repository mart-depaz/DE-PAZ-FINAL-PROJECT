from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('OFFICIAL', 'Barangay Official'),
        ('MEMBER', 'Member'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    full_name = models.CharField(_('full name'), max_length=100)
    birthdate = models.DateField(null=False, blank=False)
    age = models.PositiveIntegerField(null=True, blank=True, default=0)
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES)
    address = models.TextField(_('address'))
    contact_no = models.CharField(_('contact number'), max_length=11)
    is_pwd = models.BooleanField(_('PWD'), default=False)
    is_4ps_member = models.BooleanField(_('4Ps Member'), default=False)
    is_senior_citizen = models.BooleanField(_('Senior Citizen'), default=False)
    role = models.CharField(_('role'), max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    created_at = models.DateTimeField(auto_now_add=True)  # Add field to track signup time
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)  # Set default to timezone.now
    is_read = models.BooleanField(default=False)
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}" 