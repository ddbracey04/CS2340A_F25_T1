from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import JobApplication
from .forms import JobApplicationForm, StatusUpdateForm

@login_required
def application_list(request):
    applications = JobApplication.objects.filter(user=request.user)
    return render(request, 'home/applications/list.html', {
        'applications': applications,
        'template_data': {'title': 'My Applications'}
    })

@login_required
def application_create(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Application created successfully!')
            return redirect('application_list')
    else:
        form = JobApplicationForm()
    
    return render(request, 'home/applications/form.html', {
        'form': form,
        'template_data': {'title': 'Add Application'}
    })

@login_required
def application_edit(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('application_list')
    else:
        form = JobApplicationForm(instance=application)
    
    return render(request, 'home/applications/form.html', {
        'form': form,
        'application': application,
        'template_data': {'title': 'Edit Application'}
    })

def index(request):
    template_data = {}
    template_data['title'] = 'TODO: Title'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})

@login_required
def track_applications(request):
    """View to display all user's applications with their current status"""
    applications = JobApplication.objects.filter(user=request.user)
    
    # Get status statistics
    status_stats = applications.values('status').annotate(count=Count('status'))
    
    # Convert to dictionary for easier template access
    stats_dict = {stat['status']: stat['count'] for stat in status_stats}
    
    context = {
        'applications': applications,
        'stats': stats_dict,
        'total_applications': applications.count(),
    }
    return render(request, 'home/track_applications.html', context)

@login_required
def update_application_status(request, application_id):
    """View to update application status"""
    application = get_object_or_404(JobApplication, id=application_id, user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            old_status = application.get_status_display()
            application.status = new_status
            application.save()
            
            messages.success(request, f'Status updated from {old_status} to {application.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('track_applications')