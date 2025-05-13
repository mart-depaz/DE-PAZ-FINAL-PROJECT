# for events app
# views.py

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from accounts.decorators import official_required
from .models import Event
from accounts.models import Notification, User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import EventSerializer

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def events(request):
    return redirect('event-list')

@login_required
def event_list(request):
    is_admin_request = request.path.startswith('/admin/')
    if not is_admin_request:
        # Clean up expired events
        expired_events = Event.objects.filter(
            when__lt=timezone.now() - timezone.timedelta(hours=24)
        )
        expired_events.delete()

        # Fetch active events
        events = Event.objects.filter(when__gte=timezone.now() - timezone.timedelta(hours=24)).order_by('when')

        # Check for events starting now
        current_time = timezone.now()
        logger.debug(f"Current time: {current_time}")
        starting_events = Event.objects.filter(
            when__gte=current_time - timezone.timedelta(minutes=5),  # Widened to 5 minutes for testing
            when__lte=current_time + timezone.timedelta(minutes=5)   # Widened to 5 minutes for testing
        ).exclude(id__in=Notification.objects.filter(event__isnull=False).values('event'))

        for event in starting_events:
            logger.debug(f"Event '{event.what}' at {event.when} matches start window")
            users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
            creator_name = event.created_by.username if event.created_by else "Unknown"
            event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p').replace(f" {event.when.strftime('%I')}:", f" {event.when.strftime('%I').lstrip('0')}:")
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"Event '{event.what}' has started now! on {event_time_str}",
                    event=event,
                    timestamp=current_time
                )
            logger.info(f"Notification sent for event '{event.what}' starting now.")

        # Notify about nearing events (existing logic)
        nearing_events = Event.objects.filter(
            when__gte=timezone.now(),
            when__lte=timezone.now() + timezone.timedelta(hours=24)
        ).exclude(id__in=Notification.objects.filter(event__isnull=False).values('event'))
        for event in nearing_events:
            creator_name = event.created_by.username if event.created_by else "Unknown"
            event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p')
            hour = event.when.strftime('%I').lstrip('0')
            event_time_str = event_time_str.replace(f" {event.when.strftime('%I')}:", f" {hour}:")
            for user in User.objects.filter(role__in=['OFFICIAL', 'MEMBER']):
                Notification.objects.create(
                    user=user,
                    message=f"Event '{event.what}' is nearing on {event_time_str}, please be informed",
                    event=event,
                    timestamp=current_time
                )
    else:
        events = Event.objects.all().order_by('when')

    logger.debug(f"Events retrieved: {events}")
    context = {
        'events': events,
        'is_official': request.user.role == 'OFFICIAL',
    }
    return render(request, 'events/event_list.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event,
        'is_official': request.user.role == 'OFFICIAL',
    }
    return render(request, 'events/event_detail.html', context)

@login_required
@official_required
def add_event(request):
    if request.method == 'POST':
        what = request.POST.get('what')
        when_str = request.POST.get('when')
        where = request.POST.get('where')
        who = request.POST.get('who')

        logger.debug(f"Add Event - Received when_str: '{when_str}'")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to add an event.")
            return redirect('event-list')

        if when_str:
            when_str = ' '.join(when_str.strip().split())
            logger.debug(f"Add Event - Normalized when_str: '{when_str}'")
            try:
                when = timezone.datetime.strptime(when_str, '%B %d, %Y - %I:%M %p')
                when = timezone.make_aware(when)
                logger.debug(f"Add Event - Parsed when: {when}")
                if when < timezone.now():
                    logger.warning(f"Add Event - Attempted to set outdated time: {when}")
                    messages.error(request, "Cannot add an event with a past date and time. Please select a future date and time.")
                    return redirect('event-list')
            except ValueError as e:
                logger.error(f"Date parsing error: {e}, when_str: '{when_str}'")
                try:
                    when = timezone.datetime.strptime(when_str.split(' - ')[0], '%B %d, %Y')
                    when = when.replace(hour=12, minute=0)
                    when = timezone.make_aware(when)
                    logger.debug(f"Add Event - Defaulted to 12:00 PM: {when}")
                    if when < timezone.now():
                        logger.warning(f"Add Event - Fallback time is outdated: {when}")
                        messages.error(request, "Cannot add an event with a past date. Please select a future date.")
                        return redirect('event-list')
                except ValueError:
                    messages.error(request, "Invalid date format. Please use the date picker (e.g., 'May 10, 2025 - 02:00 PM').")
                    return redirect('event-list')
        else:
            logger.error("Add Event - No when_str provided")
            messages.error(request, "Date and time are required.")
            return redirect('event-list')

        if what and when and where and who:
            event = Event.objects.create(
                what=what,
                when=when,
                where=where,
                who=who,
                created_by=request.user
            )
            logger.debug(f"Add Event - Created event: {event}")
            current_time = timezone.now()
            users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
            creator_username = request.user.full_name
            event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p').replace(f" {event.when.strftime('%I')}:", f" {event.when.strftime('%I').lstrip('0')}:")
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"New event '{event.what}' added on {event_time_str} by {creator_username}",
                    event=event,
                    timestamp=current_time
                )
            messages.success(request, "Event added successfully.")
            return redirect('event-list')
        else:
            logger.warning("Missing required fields in add_event")
            messages.error(request, "All fields are required.")
            return redirect('event-list')
    logger.debug("add_event accessed with non-POST method")
    return redirect('event-list')

@login_required
@official_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        what = request.POST.get('what')
        when_str = request.POST.get('when')
        where = request.POST.get('where')
        who = request.POST.get('who')

        logger.debug(f"Edit Event - Received when_str: '{when_str}'")

        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to edit an event.")
            return redirect('event-list')

        if when_str:
            when_str = ' '.join(when_str.strip().split())
            logger.debug(f"Edit Event - Normalized when_str: '{when_str}'")
            try:
                when = timezone.datetime.strptime(when_str, '%B %d, %Y - %I:%M %p')
                when = timezone.make_aware(when)
                logger.debug(f"Edit Event - Parsed when: {when}")
                if when < timezone.now():
                    logger.warning(f"Edit Event - Attempted to set outdated time: {when}")
                    messages.error(request, "Cannot edit an event to a past date and time. Please select a future date and time.")
                    return redirect('event-list')
            except ValueError as e:
                logger.error(f"Date parsing error: {e}, when_str: '{when_str}'")
                try:
                    when = timezone.datetime.strptime(when_str.split(' - ')[0], '%B %d, %Y')
                    when = when.replace(hour=12, minute=0)
                    when = timezone.make_aware(when)
                    logger.debug(f"Edit Event - Defaulted to 12:00 PM: {when}")
                    if when < timezone.now():
                        logger.warning(f"Edit Event - Fallback time is outdated: {when}")
                        messages.error(request, "Cannot edit an event to a past date. Please select a future date.")
                        return redirect('event-list')
                except ValueError:
                    messages.error(request, "Invalid date format. Please use the date picker (e.g., 'May 10, 2025 - 02:00 PM').")
                    return redirect('event-list')
        else:
            logger.error("Edit Event - No when_str provided")
            messages.error(request, "Date and time are required.")
            return redirect('event-list')

        if what and when and where and who:
            event.what = what
            event.when = when
            event.where = where
            event.who = who
            event.save()
            logger.debug(f"Edit Event - Updated event: {event}")
            current_time = timezone.now()
            users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
            editor_username = request.user.full_name
            event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p').replace(f" {event.when.strftime('%I')}:", f" {event.when.strftime('%I').lstrip('0')}:")
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"Event '{event.what}' updated for {event_time_str} by {editor_username}",
                    event=event,
                    timestamp=current_time
                )
            messages.success(request, "Event updated successfully.")
            return redirect('event-list')
        else:
            logger.warning("Missing required fields in edit_event")
            messages.error(request, "All fields are required.")
            return redirect('event-list')
    logger.debug("edit_event accessed with non-POST method")
    return redirect('event-list')

@login_required
@official_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event_name = event.what
        event.delete()
        messages.success(request, f"Event '{event_name}' deleted successfully.")
        current_time = timezone.now()
        users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
        delete_username = request.user.full_name
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Event '{event_name}' deleted by {delete_username}",
                timestamp=current_time
            )
        return redirect('event-list')
    return redirect('event-list')


class IsOfficial(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'OFFICIAL'

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOfficial()]
        return [IsAuthenticated()]

    def get_queryset(self):
        logger.debug(f"EventViewSet accessed by user: {self.request.user.username}")
        if self.request.user.role == 'OFFICIAL':
            return Event.objects.all().order_by('when')
        return Event.objects.filter(when__gte=timezone.now() - timezone.timedelta(hours=24)).order_by('when')

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionError("Authentication required to create an event.")
        serializer.save(created_by=self.request.user)
        event = serializer.instance
        current_time = timezone.now()
        users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
        creator_username = self.request.user.username
        event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p').replace(f" {event.when.strftime('%I')}:", f" {event.when.strftime('%I').lstrip('0')}:")
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"New event '{event.what}' added on {event_time_str} by {creator_username}",
                event=event,
                timestamp=current_time
            )

    def perform_update(self, serializer):
        serializer.save()
        event = serializer.instance
        current_time = timezone.now()
        users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
        editor_username = self.request.user.full_name
        event_time_str = event.when.strftime('%B %d, %Y at %I:%M %p').replace(f" {event.when.strftime('%I')}:", f" {event.when.strftime('%I').lstrip('0')}:")
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Event '{event.what}' updated for {event_time_str} by {editor_username}",
                event=event,
                timestamp=current_time
            )

    def perform_destroy(self, instance):
        event_name = instance.what
        current_time = timezone.now()
        users = User.objects.filter(role__in=['OFFICIAL', 'MEMBER'])
        delete_username = self.request.user.full_name
        for user in users:
            Notification.objects.create(
                user=user,
                message=f"Event '{event_name}' deleted by {delete_username}",
                timestamp=current_time
            )
        instance.delete()