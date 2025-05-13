# for events app
# events/models.py


from django.db import models
from django.utils import timezone
from accounts.models import User  # Import the custom User model

class Event(models.Model):
    what = models.CharField(max_length=100)
    when = models.DateTimeField()
    where = models.CharField(max_length=100)
    who = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.what

    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"

    def is_expired(self):
        """Check if the event is expired (24 hours past the event time)."""
        return timezone.now() > self.when + timezone.timedelta(hours=24)