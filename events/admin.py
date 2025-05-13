# for events app
# admin.py


from django.contrib import admin
from .models import Event
from django.utils import timezone
from accounts.admin import admin_site  # Import the custom admin site

class ExpiredEventFilter(admin.SimpleListFilter):
    title = 'Expired Status'
    parameter_name = 'expired'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Expired'),
            ('no', 'Not Expired'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(when__lt=timezone.now() - timezone.timedelta(hours=24))
        if self.value() == 'no':
            return queryset.filter(when__gte=timezone.now() - timezone.timedelta(hours=24))
        return queryset

class EventAdmin(admin.ModelAdmin):
    list_display = ('what', 'when', 'where', 'who', 'created_by', 'created_at', 'updated_at', 'is_expired')
    search_fields = ('what', 'where', 'who', 'created_by__username', 'created_by__full_name')
    list_filter = ('when', ExpiredEventFilter)
    ordering = ['when']  # Sort by 'when' in ascending order

admin_site.register(Event, EventAdmin)  # Use admin_site instead of admin.site