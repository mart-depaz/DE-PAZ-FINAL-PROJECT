# for accounts app
# accounts/admin.py

from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User as DefaultUser
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from .models import User, Notification

class CustomAdminSite(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.is_admin)

    def login(self, request, extra_context=None):
        if request.user.is_authenticated and not self.has_permission(request):
            if request.user.role == 'OFFICIAL':
                return redirect('dashboard-official')
            else:
                return redirect('dashboard-member')
        return super().login(request, extra_context)

# Create an instance of the custom admin site
admin_site = CustomAdminSite(name='custom_admin')

# Unregister the default User model from the auth app (if registered)
try:
    admin_site.unregister(DefaultUser)
except admin.sites.NotRegistered:
    pass

# Register the custom User model with enhanced admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'role', 'is_admin', 'contact_no', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    list_filter = ('role', 'is_admin', 'is_pwd', 'is_4ps_member', 'is_senior_citizen', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    # Add custom buttons/links in the changelist view
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Add URLs for filtering by role
        extra_context['view_officials_url'] = f"{reverse('admin:accounts_user_changelist')}?role__exact=OFFICIAL"
        extra_context['view_members_url'] = f"{reverse('admin:accounts_user_changelist')}?role__exact=MEMBER"
        extra_context['view_all_url'] = reverse('admin:accounts_user_changelist')
        return super().changelist_view(request, extra_context=extra_context)

admin_site.register(User, UserAdmin)

# Register the Notification model
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp', 'is_read')
    search_fields = ('message', 'user__username')
    list_filter = ('is_read', 'timestamp')

admin_site.register(Notification, NotificationAdmin)