from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

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
        can_edit = request.user.is_admin() or request.user in job.users.all()
    else:
        can_edit = False
    template_data['has_applied'] = has_applied
    template_data['can_edit'] = can_edit
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


@login_required
def create_job(request):
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save()
            job.users.add(request.user)
            messages.success(request, 'Job posted successfully.')
            return redirect('jobs.show', id=job.id)
    else:
        form = JobForm()

    return render(request, 'jobs/form.html', {'form': form, 'mode': 'create'})


@login_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if not (request.user.is_admin() or request.user in job.users.all()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('jobs.show', id=job.id)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/form.html', {'form': form, 'mode': 'edit', 'job': job})
