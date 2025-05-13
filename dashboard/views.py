# for dashbaord app
# dashboard/views.py

from django.shortcuts import render, redirect
from accounts.decorators import official_required
from django.contrib.auth.decorators import login_required
from accounts.models import User, Notification
from events.models import Event
from django.utils import timezone

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'OFFICIAL':
        return redirect('dashboard-official')
    else:
        return redirect('dashboard-member')

@login_required
def official_dashboard(request):
    if request.user.role != 'OFFICIAL':
        return redirect('dashboard-member')
    
    total_males = User.objects.filter(gender='M').count()
    total_females = User.objects.filter(gender='F').count()
    total_children = User.objects.filter(age__lt=18).count()
    total_youth = User.objects.filter(age__gte=18, age__lte=35).count()
    total_senior_citizens = User.objects.filter(is_senior_citizen=True).count()
    total_pwd = User.objects.filter(is_pwd=True).count()
    
    # Fetch events for the dashboard, sorted by 'when'
    events = Event.objects.filter(when__gte=timezone.now() - timezone.timedelta(hours=24)).order_by('when')

    context = {
        'total_males': total_males,
        'total_females': total_females,
        'total_children': total_children,
        'total_youth': total_youth,
        'total_senior_citizens': total_senior_citizens,
        'total_pwd': total_pwd,
        'events': events,
        'is_official': request.user.role == 'OFFICIAL',  # Add this
    }
    return render(request, 'dashboard/official_dashboard.html', context)

@login_required
def member_dashboard(request):
    if request.user.role == 'OFFICIAL':
        return redirect('dashboard-official')
    
    total_males = User.objects.filter(gender='M').count()
    total_females = User.objects.filter(gender='F').count()
    total_children = User.objects.filter(age__lt=18).count()
    total_youth = User.objects.filter(age__gte=18, age__lte=35).count()
    total_senior_citizens = User.objects.filter(is_senior_citizen=True).count()
    total_pwd = User.objects.filter(is_pwd=True).count()
    
    # Fetch events for the dashboard, sorted by 'when'
    events = Event.objects.filter(when__gte=timezone.now() - timezone.timedelta(hours=24)).order_by('when')

    context = {
        'total_males': total_males,
        'total_females': total_females,
        'total_children': total_children,
        'total_youth': total_youth,
        'total_senior_citizens': total_senior_citizens,
        'total_pwd': total_pwd,
        'events': events,
        'is_official': request.user.role == 'OFFICIAL',  # Add this
    }
    return render(request, 'dashboard/member_dashboard.html', context)

@login_required
def profile(request):
    return render(request, 'accounts/editprofile.html')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    context = {
        'notifications': notifications,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def population(request):
    total_males = User.objects.filter(gender='M').count()
    total_females = User.objects.filter(gender='F').count()
    total_children = User.objects.filter(age__lt=18).count()
    total_youth = User.objects.filter(age__gte=18, age__lte=35).count()
    total_senior_citizens = User.objects.filter(is_senior_citizen=True).count()
    total_pwd = User.objects.filter(is_pwd=True).count()

    context = {
        'total_males': total_males,
        'total_females': total_females,
        'total_children': total_children,
        'total_youth': total_youth,
        'total_senior_citizens': total_senior_citizens,
        'total_pwd': total_pwd,
    }
    return render(request, 'dashboard/population.html', context)

def about(request):
    # Fetch all barangay officials
    officials = User.objects.filter(role='OFFICIAL').order_by('full_name')
    context = {
        'officials': officials,
    }
    return render(request, 'dashboard/about.html', context)