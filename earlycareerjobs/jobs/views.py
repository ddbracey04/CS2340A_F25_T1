
from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobSearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_applicant(request, job_id, app_id):
    job = get_object_or_404(Job, id=job_id)
    application = get_object_or_404(Application, id=app_id, job=job)
    if not (request.user.is_admin() or (request.user.is_recruiter() and request.user in job.users.all())):
        return HttpResponseForbidden()
    application.delete()
    messages.success(request, 'Applicant deleted successfully.')
    return redirect('jobs.show', id=job_id)

@login_required
def edit_applicant(request, job_id, app_id):
    job = get_object_or_404(Job, id=job_id)
    application = get_object_or_404(Application, id=app_id, job=job)
    if not (request.user.is_admin() or (request.user.is_recruiter() and request.user in job.users.all())):
        return HttpResponseForbidden()
    if request.method == 'POST':
        user_note = request.POST.get('user_note', '').strip()
        application.user_note = user_note
        application.save()
        messages.success(request, 'Applicant note updated successfully.')
        return redirect('jobs.show', id=job_id)
    return render(request, 'jobs/edit_applicant.html', {'application': application, 'job': job})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobSearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_job(request, id):
    job = get_object_or_404(Job, id=id)
    if not request.user.is_admin():
        return HttpResponseForbidden()
    job.delete()
    messages.success(request, 'Job deleted successfully.')
    return redirect('jobs.index')

def index(request):
    # search_term = request.GET.get('search')
    # if search_term:
    #     jobs = Job.objects.filter(title__icontains=search_term)
    # else:
    #     jobs = Job.objects.all()
    # template_data = {}
    # template_data['title'] = 'Jobs'
    # template_data['jobs'] = jobs


    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.all()

    # if form.is_valid():
    #     data = form.cleaned_data

    #     if data.get("title"):
    #         jobs = jobs.filter(title__icontains=data["title"])

    #     if data.get("skills"):
    #         skill_terms = [term.strip() for term in data["skills"].split(",") if term.strip()]
    #         for term in skill_terms:
    #             jobs = jobs.filter(skills__icontains=term)

    #     if data.get("city"):
    #         jobs = jobs.filter(city__iexact=data["city"])

    #     if data.get("state"):
    #         jobs = jobs.filter(state__iexact=data["state"])

    #     if data.get("country"):
    #         jobs = jobs.filter(country__iexact=data["country"])

    #     if data.get("salary_min") is not None:
    #         jobs = jobs.filter(salary_min__gte=data["salary_min"])

    #     if data.get("salary_max") is not None:
    #         jobs = jobs.filter(salary_max__lte=data["salary_max"])

    #     if data.get("work_style"):
    #         jobs = jobs.filter(work_style=data["work_style"])

    #     if data.get("visa_sponsorship"):
    #         jobs = jobs.filter(visa_sponsorship=True)

    #     template_data = {"title": "TODO: Title"}

    #     context = {
    #         "template_data": template_data,
    #         "form": form,
    #         "jobs": jobs,
    #     }
    # else:
    data = form.data

    if data.get("title") and data.get("title") != '':
        jobs = jobs.filter(title__icontains=data["title"])

    if data.get("skills") and data.get("skills") != '':
        skill_terms = [term.strip() for term in data["skills"].split(",") if term.strip()]
        for term in skill_terms:
            jobs = jobs.filter(skills__icontains=term)

    if data.get("city") and data.get("city") != '':
        jobs = jobs.filter(city__iexact=data["city"])

    if data.get("state") and data.get("state") != '':
        jobs = jobs.filter(state__iexact=data["state"])

    if data.get("country") and data.get("country") != '':
        jobs = jobs.filter(country__iexact=data["country"])

    if data.get("salary_min") is not None and data.get("salary_min") != '':
        jobs = jobs.filter(salary_min__gte=data["salary_min"])

    if data.get("salary_max") is not None and data.get("salary_max") != '':
        jobs = jobs.filter(salary_max__lte=data["salary_max"])

    if data.get("work_style") and data.get("work_style") != '':
        jobs = jobs.filter(work_style=data["work_style"])

    if data.get("visa_sponsorship") and data.get("visa_sponsorship") != '':
        jobs = jobs.filter(visa_sponsorship=True)

    template_data = {"title": "Early Career Jobs"}

    context = {
        "template_data": template_data,
        "form": form,
        "jobs": jobs,
    }

    return render(request, 'jobs/index.html', {'template_data': template_data, 'context': context})

def show(request, id):
    job = Job.objects.get(id=id)
    template_data = {}
    template_data['title'] = job.title
    template_data['job'] = job
    # Determine whether the current user has already applied to this job
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, user=request.user).exists()
        can_edit = request.user.is_admin() or (request.user.is_recruiter() and request.user in job.users.all())
    else:
        can_edit = False
    template_data['has_applied'] = has_applied
    template_data['can_edit'] = can_edit
    template_data['applications'] = Application.objects.filter(job=job)
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

        job.users.add(request.user)
        job.save()
        return redirect('jobs.show', id=id)
    else:
        return redirect('jobs.show', id=id)


@login_required
def create_job(request):
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = JobSearchForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save()
            job.users.add(request.user)
            messages.success(request, 'Job posted successfully.')
            return redirect('jobs.show', id=job.id)
    else:
        form = JobSearchForm()

    return render(request, 'jobs/form.html', {'form': form, 'mode': 'create'})


@login_required
def edit_job(request, id):
    job = get_object_or_404(Job, id=id)

    if not (request.user.is_admin() or request.user in job.users.all()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = JobSearchForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('jobs.show', id=job.id)
    else:
        form = JobSearchForm(instance=job)

    return render(request, 'jobs/form.html', {'form': form, 'mode': 'edit', 'job': job})
