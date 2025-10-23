from django.shortcuts import render, redirect, get_object_or_404
from .models import Job, Application
from .forms import JobSearchForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.urls import reverse
from map.models import Location
from map.utils import lookupLatLon

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

    if data.get("visa_sponsorship") and data.get("visa_sponsorship") != '':
        jobs = jobs.filter(visa_sponsorship=True)
        

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

    user_jobs = Job.objects.none()
    other_jobs = jobs
    if request.user.is_authenticated:
        user_jobs = jobs.filter(users=request.user)
        other_jobs = jobs.exclude(users=request.user)

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
