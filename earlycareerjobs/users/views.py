from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser
from .models import JobSeekerProfile, ProfilePrivacy
from .forms import PrivacySettingsForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            if user.role == CustomUser.Role.RECRUITER:
                user.company_name = form.cleaned_data.get('company_name')
            elif user.role == CustomUser.Role.JOB_SEEKER:
                if 'resume' in request.FILES:
                    user.resume = request.FILES['resume']
            
            user.save()
            
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, 'Registration successful!')
            return redirect('home.index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == CustomUser.Role.ADMIN:
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    return wrap

@login_required
@admin_required
def user_management(request):
    users = CustomUser.objects.all()
    return render(request, 'admin/user_management.html', {'users': users})


@login_required
@admin_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in [role[0] for role in CustomUser.Role.choices]:
            user.role = role
            user.save()
            messages.success(request, f'The role of user {user.username} has been updated to {user.get_role_display()}')
            return redirect('user_management')
    
    return render(request, 'admin/edit_user.html', {'user': user})

@login_required
@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activate" if user.is_active else "inactivate"
    messages.success(request, f'User {user.username} is {status}')
    return redirect('user_management')

@login_required
def privacy_settings(request):
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, "Please create your profile first.")
        return redirect('profile_create')
    
    # get or create privacy settings
    privacy, created = ProfilePrivacy.objects.get_or_create(profile=profile)
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=privacy)
        if form.is_valid():
            form.save()
            messages.success(request, "Privacy settings updated successfully!")
            return redirect('privacy_settings')
    else:
        form = PrivacySettingsForm(instance=privacy)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'users/privacy_settings.html', context)