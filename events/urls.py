from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/events', views.EventViewSet, basename='event')

urlpatterns = [
    path('', views.events, name='events'),
    path('list/', views.event_list, name='event-list'),
    path('detail/<int:event_id>/', views.event_detail, name='event-detail'),
    path('add/', views.add_event, name='add-event'),
    path('edit/<int:event_id>/', views.edit_event, name='edit-event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete-event'),
] + router.urls