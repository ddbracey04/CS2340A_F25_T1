from django.shortcuts import render, redirect
from .models import Job, Application
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        jobs = Job.objects.filter(title__icontains=search_term)
    else:
        jobs = Job.objects.all()
    template_data = {}
    template_data['title'] = 'Jobs'
    template_data['jobs'] = jobs
    return render(request, 'jobs/index.html', {'template_data': template_data})

def show(request, id):
    job = Job.objects.get(id=id)
    template_data = {}
    template_data['title'] = job.title
    template_data['job'] = job
    # Determine whether the current user has already applied to this job
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, user=request.user).exists()
    template_data['has_applied'] = has_applied
    return render(request, 'jobs/show.html', {'template_data': template_data})

@login_required
def start_application(request, id):
    if request.method == 'POST': #and request.POST['note'] != '' shouldnt be necessary to require user to input a personal note if they don't want to
        job = Job.objects.get(id=id)
        application = Application()
        application.user_note = request.POST['user_note']
        application.job = job
        application.user = request.user
        application.save()
        return redirect('jobs.show', id=id)
    else:
        return redirect('jobs.show', id=id)