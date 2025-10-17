from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobSearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
# from django.http import JsonResponse
from django.db.models import Count
from map.models import Location
from map.utils import lookupLatLon

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
        application.status = 'APPLIED'
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
        job = Job()
        job.lat = 0
        job.lon = 0
        job.save()
        form = JobSearchForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            job.users.add(request.user)

            try:
                location = Location.objects.get(city=job.city, state=job.state, country=job.country)
            except Location.DoesNotExist:
                location = Location()
                location.city = job.city
                location.state = job.state
                location.country = job.country
                location.lat, location.lon = lookupLatLon(cityName=job.city, stateName=job.state, countryName=job.country)
                location.save()
            job.lat = location.lat
            job.lon = location.lon
            job.save()


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

            if form.has_changed() and ("city" in form.changed_data or "state" in form.changed_data or "country" in form.changed_data):
                try:
                    location = Location.objects.get(city=job.city, state=job.state, country=job.country)
                except Location.DoesNotExist:
                    location = Location()
                    location.city = job.city
                    location.state = job.state
                    location.country = job.country
                    location.lat, location.lon = lookupLatLon(cityName=job.city, stateName=job.state, countryName=job.country)
                    location.save()
                job.lat = location.lat
                job.lon = location.lon
                job.save()

            form.save()

            messages.success(request, 'Job updated successfully.')
            return redirect('jobs.show', id=job.id)
    else:
        form = JobSearchForm(instance=job)

    return render(request, 'jobs/form.html', {'form': form, 'mode': 'edit', 'job': job})



@login_required
def application_list(request, id):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'home/applications/list.html', {
        'applications': applications,
        'template_data': {'title': 'My Applications'}
    })

# @login_required
# def application_edit(request, id, pk):
#     application = get_object_or_404(Application, pk=pk, user=request.user)

#     if request.method == 'POST':
#         form = ApplicationForm(request.POST, instance=application)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Application updated successfully!')
#             return redirect('application_list')
#     else:
#         form = ApplicationForm(instance=application)

#     return render(request, 'home/applications/form.html', {
#         'form': form,
#         'application': application,
#         'template_data': {'title': 'Edit Application'}
#     })

@login_required
def track_applications(request, id):
    """View to display all user's applications with their current status"""
    applications = Application.objects.filter(user=request.user)

    # Get status statistics
    status_stats = applications.values('status').annotate(count=Count('status'))

    # Convert to dictionary for easier template access
    stats_dict = {stat['status']: stat['count'] for stat in status_stats}

    context = {
        'applications': applications,
        'stats': stats_dict,
        'total_applications': applications.count(),

    }
    return render(request, 'jobs/track_applications.html', context)

@login_required
def update_application_status(request, id, application_id):
    """View to update application status"""
    application = get_object_or_404(Application, id=application_id, user=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            old_status = application.get_status_display()
            application.status = new_status
            application.save()

            messages.success(request, f'Status updated from {old_status} to {application.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected')

    return redirect('jobs.track_applications')
