# for accounts app
# accounts/views.py


import logging
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from .models import User, Notification
from .forms import CreatePasswordForm, SignUpForm, EditProfileForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.http import HttpResponseForbidden
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from accounts.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, NotificationSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Set up logging
logger = logging.getLogger(__name__)

# Custom Pagination Class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def signup(request):
    if request.user.is_authenticated:
        auth_logout(request)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.role:
                user.role = 'MEMBER'
            user.is_admin = False
            user.set_unusable_password()
            base_username = user.email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
            signup_time = timezone.now()  # Capture signup time
            try:
                user.save()
                officials = User.objects.filter(role='OFFICIAL')
                formatted_time = signup_time.astimezone(timezone.get_current_timezone()).strftime('%B %d, %Y at %I:%M %p')
                for official in officials:
                    Notification.objects.create(
                        user=official,
                        message=f"New user {user.full_name} ({user.role}) signed up on {formatted_time}",
                        timestamp=signup_time  # Use captured signup time
                    )
                logger.info(f"User {user.username} signed up successfully at {formatted_time}")
            except IntegrityError as e:
                logger.error(f"IntegrityError during signup for {username}: {str(e)}")
                form.add_error(None, "Username already exists")
                return render(request, 'accounts/signup.html', {
                    'form': form,
                    'gender_choices': User.GENDER_CHOICES,
                })
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            logger.debug(f"Logged in user after signup: {request.user.username} (ID: {request.user.id})")
            return redirect('create-password', user_id=user.id)
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {
        'form': form,
        'gender_choices': User.GENDER_CHOICES,
    })


@login_required
def create_password(request, user_id):
    if request.user.id != user_id:
        logger.warning(f"User {request.user.id} attempted to set password for user {user_id}")
        return HttpResponseForbidden("You can only set your own password")
    if request.user.is_superuser:
        logger.warning(f"Superuser {request.user.id} attempted to change password via create_password")
        return HttpResponseForbidden("Superuser password cannot be changed via this page")

    if request.method == 'POST':
        form = CreatePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            request.user.set_password(password)
            request.user.save()
            user = authenticate(
                username=request.user.username,
                password=password
            )
            if user is not None:
                auth_login(request, user)
                logger.info(f"User {user.username} set their password and logged in")
            if request.user.role == 'OFFICIAL':
                return redirect('dashboard-official')
            else:
                return redirect('dashboard-member')
        else:
            logger.error(f"Create password form errors for user {request.user.username}: {form.errors}")
    else:
        form = CreatePasswordForm()

    return render(request, 'accounts/signup_password.html', {
        'form': form,
        'user_id': user_id
    })

def password_reset(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"Password reset attempted for non-existent user ID {user_id}")
        messages.error(request, "Invalid user")
        return redirect('password-reset')

    if request.method == 'POST':
        form = CreatePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            user.set_password(password)
            user.save()
            user = authenticate(username=user.username, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, "Password updated successfully!")
                request.session['welcome_message'] = f"Welcome, {user.full_name}"
                request.session['user_role'] = user.get_role_display()
                logger.info(f"User {user.username} reset their password and logged in")
                if user.role == 'ADMIN':
                    pass
                elif user.role == 'OFFICIAL':
                    return redirect('dashboard-official')
                else:
                    return redirect('dashboard-member')
    else:
        form = CreatePasswordForm()

    return render(request, 'accounts/password_reset.html', {
        'form': form,
        'user_id': user_id
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        logger.debug(f"Username authentication attempt: {username}, Result: {user}")

        if user is None:
            try:
                user_with_email = User.objects.get(email__iexact=username)
                user = authenticate(request, username=user_with_email.username, password=password)
                logger.debug(f"Email authentication attempt: {username}, Username: {user_with_email.username}, Result: {user}")
            except User.DoesNotExist:
                logger.debug(f"Email not found: {username}")

        if user is not None:
            auth_login(request, user)
            request.session['welcome_message'] = f"Welcome, {user.full_name}"
            request.session['user_role'] = user.get_role_display()
            logger.info(f"User {user.username} logged in successfully")

            if user.role == 'OFFICIAL':
                return redirect('dashboard-official')
            else:
                return redirect('dashboard-member')
        else:
            logger.warning(f"Failed login attempt for username/email: {username}")
            messages.error(request, "Invalid username/email or password")
            return render(request, 'accounts/login.html', {'error': True})

    return render(request, 'accounts/login.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            logger.info(f"User {user.username} initiated password reset via forgot password")
            return redirect('reset-your-password', user_id=user.id)
        except User.DoesNotExist:
            logger.warning(f"Forgot password attempt with non-existent email: {email}")
            messages.error(request, "Email not found.")
            return redirect('password-reset')
    return render(request, 'accounts/forgot_password.html')


def edit_member(request, user_id):
    user = get_object_or_404(User, id=user_id, role='MEMBER')
    if request.method == 'POST':
        form = SignUpForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Member info updated.")
            logger.info(f"Official {request.user.username} updated member {user.username}")
            return redirect('member-list')
    else:
        form = SignUpForm(instance=user)

    return render(request, 'accounts/edit_member.html', {
        'form': form,
        'user': user
    })


def delete_member(request, user_id):
    user = get_object_or_404(User, id=user_id, role='MEMBER')
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Member deleted.")
        logger.info(f"Official {request.user.username} deleted member ID {user_id}")
        return redirect('member-list')
    return render(request, 'accounts/confirm_delete.html', {'user': user})


def member_list(request):
    members = User.objects.filter(role='MEMBER')
    return render(request, 'accounts/member_list.html', {'members': members})

@login_required
def logout_view(request):
    if request.method == 'POST':
        username = request.user.username
        auth_logout(request)
        logger.info(f"User {username} logged out")
        return redirect('dashboard-dashboard')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            logger.debug(f"Form saved successfully.")
            messages.success(request, "Profile updated successfully!")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('partial'):
                form = EditProfileForm(instance=user)
                return render(request, 'accounts/editprofile_partial.html', {'form': form})
            return redirect('edit-profile')
        else:
            logger.error(f"Form validation failed: {form.errors}")
            messages.error(request, "Failed to update profile. Please check the form.")
    else:
        form = EditProfileForm(instance=request.user)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('partial'):
        return render(request, 'accounts/editprofile_partial.html', {'form': form})
    
    return render(request, 'accounts/editprofile_full.html', {'form': form})

@login_required
def notifications(request):
    # Fetch notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Mark all notifications as read when the page is viewed
    unread_notifications = notifications.filter(is_read=False)
    if unread_notifications.exists():
        unread_notifications.update(is_read=True)
        logger.info(f"Marked {unread_notifications.count()} notifications as read for user {request.user.username}")

    context = {
        'notifications': notifications,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()  # Permanently delete the notification
        logger.info(f"Notification {notification_id} deleted by user {request.user.username}")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()  # Permanently delete all notifications
        logger.info(f"Deleted {count} notifications for user {request.user.username}")
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# API ViewSets
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'full_name', 'email']

    def get_queryset(self):
        if self.request.user.role == 'OFFICIAL':
            return User.objects.filter(role='MEMBER')
        return User.objects.filter(id=self.request.user.id)

    def perform_destroy(self, instance):
        # Notify officials when a user is deleted via API
        current_time = timezone.now()
        users = User.objects.filter(role='OFFICIAL')
        deleter_username = self.request.user.username
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"User '{instance.username}' deleted by {deleter_username}",
                timestamp=current_time
            )
        instance.delete()

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_read']
    search_fields = ['message']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Notify the user that a notification was deleted (optional, depending on your use case)
        current_time = timezone.now()
        Notification.objects.create(
            user=self.request.user,
            message=f"Notification '{instance.message[:20]}...' deleted by you",
            timestamp=current_time
        )
        instance.delete()