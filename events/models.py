#for events app
#models.py



from django.db import models
from django.utils import timezone
from accounts.models import User
from django.core.exceptions import ValidationError

class Event(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('postponed', 'Postponed'),
    ]
    
    what = models.CharField(max_length=100)
    when = models.DateTimeField()
    where = models.CharField(max_length=100)
    who = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {self.status}. Must be one of {list(dict(self.STATUS_CHOICES).keys())}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.what} ({self.get_status_display()})"

    def is_expired(self):
        """Check if the event is expired (either past its end time or older than 24 hours)."""
        if self.status in ['done', 'postponed']:
            return False
        current_time = timezone.now()
        return (current_time > self.when) or (current_time > self.when + timezone.timedelta(hours=24))