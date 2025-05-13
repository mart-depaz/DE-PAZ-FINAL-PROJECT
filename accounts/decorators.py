#for accounts app
# accounts/decorators.py


from django.shortcuts import redirect

def official_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # You'll need to implement login
        if request.user.role != 'OFFICIAL':
            return redirect('dashboard-dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper