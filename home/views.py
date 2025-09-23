from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobApplication
from django.forms import ModelForm

class JobApplicationForm(ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'position', 'status', 'notes']

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
