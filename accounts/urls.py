# for accounts app
# accounts/urls.py

from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, NotificationViewSet



router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('create-password/<int:user_id>/', views.create_password, name='create-password'),
    path('members/edit/<int:user_id>/', views.edit_member, name='edit-member'),
    path('members/delete/<int:user_id>/', views.delete_member, name='delete-member'),
    path('members/', views.member_list, name='member-list'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='password-reset'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-your-password/<int:user_id>/', views.password_reset, name='reset-your-password'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', csrf_exempt(views.mark_notification_read), name='mark-notification-read'),
    path('notifications/mark-all-read/', csrf_exempt(views.mark_all_notifications_read), name='mark-all-notifications-read'),
    path('api/', include(router.urls)),
]