from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import CustomUser
from jobs.models import Application, Job

from home.models import Profile
from .forms import CandidateSearchForm
from django.db.models import Q

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
            return redirect('users.user_management')
    
    return render(request, 'admin/edit_user.html', {'user': user})

@login_required
@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} has been {status}')
    return redirect('users.user_management')

@login_required
@admin_required
def edit_user_profile(request, user_id):
    from home.forms import ProfileForm
    
    user_obj = get_object_or_404(CustomUser, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user_obj)
    
    if request.method == 'POST':
        # Update user fields
        user_obj.first_name = request.POST.get('first_name', '')
        user_obj.last_name = request.POST.get('last_name', '')
        user_obj.email = request.POST.get('email', user_obj.email)
        user_obj.phone_number = request.POST.get('phone_number', '')
        
        if user_obj.is_recruiter():
            user_obj.company_name = request.POST.get('company_name', '')
        
        user_obj.save()
        
        # Update profile
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, f'Profile for {user_obj.username} has been updated successfully')
            return redirect('users.user_management')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'admin/edit_user_profile.html', {
        'user_obj': user_obj,
        'profile_form': profile_form
    })

@login_required
def view_jobs(request):

    applications = Application.objects.filter(user=request.user).select_related('job')
    context = {
        'applications': applications,
        'jobs': Job.objects.all(),
    }
    
    if request.user.is_job_seeker():
        return render(request, 'job_seeker_pages/view_jobs.html', context)
    else:
        return render(request, 'recruiter_pages/view_jobs.html', context)


# Recruiter: Search for candidates by skills, location, and projects
@login_required
def candidate_search(request):
    if not request.user.is_recruiter():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home.index')

    form = CandidateSearchForm(request.GET or None)
    results = []
    query = Q()
    if form.is_valid() and (form.cleaned_data.get('skills') or form.cleaned_data.get('location') or form.cleaned_data.get('projects')):
        skills = form.cleaned_data.get('skills', '').strip()
        location = form.cleaned_data.get('location', '').strip()
        projects = form.cleaned_data.get('projects', '').strip()

        if skills:
            for skill in [s.strip() for s in skills.split(',') if s.strip()]:
                query &= Q(skills__icontains=skill)
        if location:
            query &= Q(user__profile__headline__icontains=location) | Q(user__profile__experience__icontains=location)
        if projects:
            for project in [p.strip() for p in projects.split(',') if p.strip()]:
                query &= Q(experience__icontains=project)

        results = Profile.objects.filter(query, user__role=CustomUser.Role.JOB_SEEKER)

    return render(request, 'recruiter_pages/candidate_search.html', {
        'form': form,
        'results': results,
    })