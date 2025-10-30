from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import (
    JobSearchForm,
    JobTitleForm,
    JobDescriptionForm,
    JobSkillsForm,
    JobLocationForm,
    JobSalaryForm,
    JobImageForm,
    JobWorkStyleForm,
    JobVisaForm,
)
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.urls import reverse
from map.models import Location
from map.utils import lookupLatLon
import json

FIELD_FORM_CONFIG = {
    "title": {
        "form_class": JobTitleForm,
        "prefix": "title",
        "success_message": "Job title updated.",
    },
    "description": {
        "form_class": JobDescriptionForm,
        "prefix": "description",
        "success_message": "Job description updated.",
    },
    "skills": {
        "form_class": JobSkillsForm,
        "prefix": "skills",
        "success_message": "Skills updated.",
    },
    "location": {
        "form_class": JobLocationForm,
        "prefix": "location",
        "success_message": "Location updated.",
    },
    "salary": {
        "form_class": JobSalaryForm,
        "prefix": "salary",
        "success_message": "Salary range updated.",
    },
    "work_style": {
        "form_class": JobWorkStyleForm,
        "prefix": "workstyle",
        "success_message": "Work style updated.",
    },
    "visa": {
        "form_class": JobVisaForm,
        "prefix": "visa",
        "success_message": "Visa sponsorship updated.",
    },
    "image": {
        "form_class": JobImageForm,
        "prefix": "image",
        "success_message": "Job image updated.",
    },
}

# Admin/Recruiter functions for managing applicants
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
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.all()
    data = form.data

    # Basic filters
    if data.get("title") and data.get("title") != '':
        jobs = jobs.filter(title__icontains=data["title"])

    # Skills filtering with bubble support
    text_skills = data.get("skills", "").strip()
    bubble_skills = request.GET.getlist('skill')  # Get list of bubble skills
    skills_mode = data.get("skills_mode", "AND")
    
    all_skill_terms = []
    if text_skills:
        all_skill_terms.extend([s.strip() for s in text_skills.split(",") if s.strip()])
    if bubble_skills:
        all_skill_terms.extend([s.strip() for s in bubble_skills if s.strip()])
    
    if all_skill_terms:
        if skills_mode == "OR":
            # OR mode: match any skill
            q_objects = Q()
            for term in all_skill_terms:
                q_objects |= Q(skills__icontains=term)
            jobs = jobs.filter(q_objects)
        else:
            # AND mode: match all skills (default)
            for term in all_skill_terms:
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

    # Calculate distance from user's profile location if user is a job seeker
    from map.utils import haversine
    user_jobs = Job.objects.none()
    other_jobs = jobs
    
    if request.user.is_authenticated and request.user.is_job_seeker():
        from home.models import Profile
        try:
            profile = Profile.objects.get(user=request.user)
            if profile.lat and profile.lon:
                # Calculate distance for all jobs
                jobs_list = list(jobs)  # Convert QuerySet to list to allow modification
                for job in jobs_list:
                    if job.lat and job.lon:
                        try:
                            dist = haversine(float(profile.lat), float(profile.lon), float(job.lat), float(job.lon))
                            job.distance = round(dist, 1)
                        except (ValueError, TypeError) as e:
                            print(f"Error calculating distance for job {job.id}: {e}")
                            job.distance = None
                    else:
                        job.distance = None
                jobs = jobs_list  # Replace QuerySet with list
                
                # Split jobs into user_jobs and other_jobs
                user_jobs = [j for j in jobs_list if request.user in j.users.all()]
                other_jobs = [j for j in jobs_list if request.user not in j.users.all()]
        except Profile.DoesNotExist:
            # If no profile, use default QuerySet filtering
            user_jobs = jobs.filter(users=request.user)
            other_jobs = jobs.exclude(users=request.user)
    elif request.user.is_authenticated:
        # For non-job-seekers, use QuerySet filtering
        user_jobs = jobs.filter(users=request.user)
        other_jobs = jobs.exclude(users=request.user)
        

    # Aggregate top skills for suggestions
    all_jobs = Job.objects.all()
    skills_set = set()
    for job in all_jobs:
        if job.skill_list:
            skills_set.update(job.skill_list)
    all_skills = sorted(skills_set)[:100]  # Top 100 skills

    template_data = {
        "title": "Early Career Jobs",
        "active_skills": all_skill_terms,
        "skills_mode": skills_mode,
        "all_skills": all_skills,
    }

    context = {
        "template_data": template_data,
        "form": form,
        "jobs": jobs,
        "user_jobs": user_jobs,
        "other_jobs": other_jobs,
    }

    # Make recommended jobs list for candidates
    # Recommendation is based on overlap between the jobs skills and the applicants profile skills.
    recommended = []
    hide_recommendations = request.session.get('hide_job_recommendations', False)
    if request.user.is_authenticated and request.user.is_job_seeker():
        profile = getattr(request.user, 'home_profile', None)
        candidate_skills_lower = set([s.lower() for s in profile.skill_list]) if profile and profile.skill_list else set()
        if candidate_skills_lower:
            for job in jobs:
                job_skills_list = job.skill_list or []
                job_skills_lower = {s.lower(): s for s in job_skills_list}
                common_lower = set(job_skills_lower.keys()) & candidate_skills_lower
                if common_lower and not Application.objects.filter(job=job, user=request.user).exists(): #Don't add jobs the user has already applied to
                    # Use original casing from the job's skill list for display
                    common_original = [job_skills_lower[lk] for lk in sorted(common_lower)]
                    recommended.append({
                        'job': job,
                        'match_count': len(common_lower),
                        'common_skills': common_original,
                    })
            # sort by number of matches
            recommended.sort(key=lambda x: (-x['match_count']))
    # limit to top 3 because that sounds reasonable?
    hide_recommendations = request.session.get('hide_job_recommendations', False)
    template_data['recommendations_available'] = bool(recommended)

    if hide_recommendations:
        template_data['recommended_jobs'] = []
    else:
        template_data['recommended_jobs'] = recommended[:3]
    template_data['recommendations_hidden'] = hide_recommendations and bool(recommended)

    return render(request, 'jobs/index.html', {'template_data': template_data, 'context': context})


@login_required
def hide_recommendations(request):
    if request.user.is_job_seeker() or request.user.is_admin():
        request.session['hide_job_recommendations'] = True
        request.session.modified = True
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('jobs.index'))


@login_required
def show_recommendations(request):
    if 'hide_job_recommendations' in request.session:
        del request.session['hide_job_recommendations']
        request.session.modified = True
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('jobs.index'))

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
    applications = Application.objects.filter(job=job)
    template_data['applications'] = applications

    # Make recommended candidates list
    # Recommendation is based on overlap between the jobs skills and the applicants profile skills.
    recommended = []
    if request.user.is_authenticated and request.user.is_recruiter():
        job_skills_list = job.skill_list or []
        job_skills_lower = {s.lower(): s for s in job_skills_list}  # map lower->original
        if job_skills_lower:
            for app in applications:
                user = app.user
                profile = getattr(user, 'home_profile', None)
                if not profile:
                    continue
                candidate_skills_lower = {s.lower(): s for s in profile.skill_list or []}
                common_lower = set(job_skills_lower.keys()) & set(candidate_skills_lower.keys())
                if common_lower:
                    common_original = [candidate_skills_lower[lk] for lk in sorted(common_lower)]
                    recommended.append({
                        'user': user,
                        'match_count': len(common_lower),
                        'common_skills': common_original,
                        'application': app,
                    })
            # sort by number of matches then application date
            recommended.sort(key=lambda x: (-x['match_count'], x['application'].date))
    # limit to top 3 because that sounds reasonable?
    template_data['recommended_candidates'] = recommended[:3]

    forms_context = {}
    if request.user.is_authenticated and (request.user.is_admin() or request.user in job.users.all()):
        forms_context = {
            'title_form': FIELD_FORM_CONFIG['title']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['title']['prefix']),
            'description_form': FIELD_FORM_CONFIG['description']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['description']['prefix']),
            'skills_form': FIELD_FORM_CONFIG['skills']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['skills']['prefix']),
            'location_form': FIELD_FORM_CONFIG['location']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['location']['prefix']),
            'salary_form': FIELD_FORM_CONFIG['salary']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['salary']['prefix']),
            'work_style_form': FIELD_FORM_CONFIG['work_style']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['work_style']['prefix']),
            'visa_form': FIELD_FORM_CONFIG['visa']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['visa']['prefix']),
            'image_form': FIELD_FORM_CONFIG['image']['form_class'](instance=job, prefix=FIELD_FORM_CONFIG['image']['prefix']),
        }

    context = {
        'template_data': template_data,
        'forms': forms_context,
    }

    return render(request, 'jobs/show.html', context)


@login_required
@require_POST
def update_job_field(request, id, field):
    job = get_object_or_404(Job, id=id)
    if not (request.user.is_admin() or request.user in job.users.all()):
        return HttpResponseForbidden()

    config = FIELD_FORM_CONFIG.get(field)
    if not config:
        raise Http404()

    form_class = config["form_class"]
    form = form_class(request.POST, request.FILES, instance=job, prefix=config["prefix"])

    if form.is_valid():
        job = form.save(commit=False)
        location_changed = field == "location" and form.has_changed()
        job.save()

        if location_changed:
            if job.city or job.state or job.country:
                try:
                    location = Location.objects.get(city=job.city, state=job.state, country=job.country)
                except Location.DoesNotExist:
                    location = Location(
                        city=job.city,
                        state=job.state,
                        country=job.country,
                    )
                    try:
                        lat, lon = lookupLatLon(cityName=job.city, stateName=job.state, countryName=job.country)
                    except Exception:
                        lat, lon = (0, 0)
                    location.lat = lat
                    location.lon = lon
                    location.save()
                job.lat = location.lat
                job.lon = location.lon
            else:
                job.lat = 0
                job.lon = 0
            job.save(update_fields=["lat", "lon"])

        messages.success(request, config["success_message"])
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    return redirect('jobs.show', id=id)


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
    applications = (
        Application.objects.filter(user=request.user)
        .select_related('job')
        .prefetch_related('job__users')
        .order_by('-date')
    )

    # Get status statistics
    status_stats = applications.values('status').annotate(count=Count('status'))

    # Convert to dictionary for easier template access
    stats_dict = {stat['status']: stat['count'] for stat in status_stats}

    # Prepare Kanban data structure
    status_lookup = dict(Application.STATUS_CHOICES)
    kanban_columns = [
        {
            "key": status_key,
            "label": status_lookup.get(status_key, status_key.title()),
            "applications": [],
        }
        for status_key, _ in Application.STATUS_CHOICES
    ]

    column_index_map = {column["key"]: idx for idx, column in enumerate(kanban_columns)}

    for application in applications:
        recruiter_company = next(
            (
                user.company_name
                for user in application.job.users.all()
                if user.is_recruiter()
            ),
            "",
        )
        application.company_name = recruiter_company
        idx = column_index_map.get(application.status)
        if idx is not None:
            kanban_columns[idx]["applications"].append(application)

    for column in kanban_columns:
        column["count"] = len(column["applications"])

    context = {
        'stats': stats_dict,
        'total_applications': applications.count(),
        'kanban_columns': kanban_columns,
        'status_lookup': status_lookup,
    }
    return render(request, 'jobs/track_applications.html', context)

# @login_required
# def update_application_status(request, application_id):
#     """View to update application status"""
#     application = get_object_or_404(Application, id=application_id, user=request.user)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')
#         if new_status in dict(Application.STATUS_CHOICES):
#             old_status = application.get_status_display()
#             application.status = new_status
#             application.save()

#             messages.success(request, f'Status updated from {old_status} to {application.get_status_display()}')
#         else:
#             messages.error(request, 'Invalid status selected')

#     return redirect('jobs.track_applications')

@login_required
def update_application_status(request, application_id, new_status):
    """View to update application status"""
    application = get_object_or_404(Application, id=application_id)

    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()
    else:
        print(new_status, "not in the application status choices")

    return redirect('jobs.show', id=application.job.id)


@login_required
@require_POST
def update_application_status_ajax(request, application_id):
    """AJAX endpoint to update an application's status for the authenticated user."""
    application = get_object_or_404(Application, id=application_id, user=request.user)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = {}

    new_status = payload.get("status") or request.POST.get("status")
    valid_statuses = dict(Application.STATUS_CHOICES)

    if new_status not in valid_statuses:
        return JsonResponse(
            {"success": False, "error": "Invalid status value."},
            status=400,
        )

    previous_status = application.status
    application.status = new_status
    application.save(update_fields=["status"])

    # Recalculate stats for dashboard widgets
    status_stats = (
        Application.objects.filter(user=request.user)
        .values("status")
        .annotate(count=Count("status"))
    )
    stats_dict = {stat["status"]: stat["count"] for stat in status_stats}

    return JsonResponse(
        {
            "success": True,
            "application_id": application.id,
            "status": new_status,
            "status_display": application.get_status_display(),
            "previous_status": previous_status,
            "stats": stats_dict,
            "total_applications": sum(stats_dict.values()),
        }
    )
