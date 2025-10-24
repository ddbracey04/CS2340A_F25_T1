from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from map.utils import lookupLatLon
from users.models import CustomUser

from .forms import CandidateSearchForm, EducationForm, ProfileForm
from .models import Education, Profile


def index(request):
    return render(request, "home/index.html")


def about(request):
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            profile.lat, profile.lon = lookupLatLon(profile.city, profile.state, profile.country)
            profile.save()
            return redirect('profile.view', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    education_form = EducationForm()
    user_education = Education.objects.filter(user=request.user).order_by('pk')

    return render(request, 'home/profile_form.html', {
        'form': form,
        'education_form': education_form,
        'user_education': user_education,
    })


@login_required
def save_education(request, education_id=None):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    instance = None
    if education_id:
        try:
            instance = Education.objects.get(pk=education_id, user=request.user)
        except Education.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Education entry not found.'}, status=404)

    form = EducationForm(request.POST, instance=instance)
    if not form.is_valid():
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    education_instance = form.save(commit=False)
    education_instance.user = request.user
    education_instance.save()

    return JsonResponse({
        'status': 'success',
        'action': 'updated' if education_id else 'created',
        'level': education_instance.get_level_display(),
        'degree': education_instance.degree,
        'institution': education_instance.institution,
        'id': education_instance.id,
        'form_data': form.cleaned_data,
    })


def profile_view(request, username):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    user_education = Education.objects.filter(user=user).order_by('pk')
    return render(request, 'home/profile_view.html', {
        'profile': profile,
        'owner': user,
        'user_education': user_education,
    })


@login_required
def delete_education(request, education_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

    try:
        edu_instance = Education.objects.get(pk=education_id, user=request.user)
        edu_instance.delete()
        return JsonResponse({'status': 'success', 'id': education_id})
    except Education.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Education entry not found.'}, status=404)
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=500)

@login_required
def delete_education(request, education_id):
    if request.method == 'POST':
        try:
            edu_instance = Education.objects.get(pk=education_id, user=request.user)
            edu_instance.delete()
            return JsonResponse({'status': 'success', 'id': education_id})
        except Education.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Education entry not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required
def search_candidates(request):
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return HttpResponseForbidden()

    form = CandidateSearchForm(request.GET or None)
    
    # Get bubble skills parameters
    bubble_skills = request.GET.getlist('skill')
    
    # Get job_id if searching for a specific job
    job_id = request.GET.get('job_id')
    job = None
    if job_id:
        from jobs.models import Job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            job = None
    
    # Get recruiter's jobs for the dropdown
    recruiter_jobs = []
    if request.user.is_recruiter():
        from jobs.models import Job, Application
        from django.db.models import Count
        # Get jobs with application counts
        recruiter_jobs = Job.objects.filter(users=request.user).annotate(
            applicant_count=Count('application')
        ).order_by('-date')
    
    # Get all unique skills for autocomplete
    all_profiles = Profile.objects.filter(user__role=CustomUser.Role.JOB_SEEKER)
    skills_set = set()
    for profile in all_profiles:
        if profile.skill_list:
            skills_set.update(profile.skill_list)
    all_skills = sorted(skills_set)[:100]  # Top 100 skills
    
    if form.is_valid():
        data = form.cleaned_data
    else:
        data = {
            'experience': '',
            'skills_mode': 'OR',
            'location': '',
            'work_style': '',
            'sort_by': CandidateSearchForm.SORT_CHOICES[0][0],
        }
        form = CandidateSearchForm(initial=data)

    profiles = Profile.objects.select_related('user').filter(user__role=CustomUser.Role.JOB_SEEKER)
    
    # If a specific job is selected, filter to only show applicants for that job
    if job:
        from jobs.models import Application
        applicant_user_ids = Application.objects.filter(job=job).values_list('user_id', flat=True)
        profiles = profiles.filter(user_id__in=applicant_user_ids)

    # Bubble skills filter (AND/OR logic)
    skills_mode = request.GET.get('skills_mode', 'OR')
    if bubble_skills:
        if skills_mode == 'AND':
            # AND logic: must match all skills
            for skill in bubble_skills:
                skill = skill.strip()
                if skill:
                    profiles = profiles.filter(skills__icontains=skill)
        else:
            # OR logic: match any skill
            skill_query = Q()
            for skill in bubble_skills:
                skill = skill.strip()
                if skill:
                    skill_query |= Q(skills__icontains=skill)
            profiles = profiles.filter(skill_query)
    
    # Experience text search
    experience = data.get('experience')
    if experience:
        profiles = profiles.filter(experience__icontains=experience)
    
    # Get distance parameter for filtering
    distance_param = data.get('distance')
    if not distance_param or distance_param == 0:
        distance_param = 50  # Default to 50 miles
    
    # Calculate distance from job location if job_id is provided
    from map.utils import haversine
    if job and job.lat and job.lon:
        # Calculate distance for all profiles and filter by distance
        profiles_list = []
        for profile in profiles:
            if profile.lat and profile.lon:
                try:
                    dist = haversine(float(job.lat), float(job.lon), float(profile.lat), float(profile.lon))
                    profile.distance = round(dist, 1)
                    # Apply distance filter
                    if profile.distance <= distance_param:
                        profiles_list.append(profile)
                except (ValueError, TypeError) as e:
                    print(f"Error calculating distance for profile {profile.id}: {e}")
            # If profile has no location, don't include it when filtering by job
        profiles = profiles_list  # Replace QuerySet with filtered list
    else:
        # Location filter with distance calculation (original logic for manual search)
        location = data.get('location')
        
        if location and location.strip():
            from map.utils import lookupLatLon
            
            # Parse location input (try to split by comma)
            location_parts = [part.strip() for part in location.split(',')]
            city = location_parts[0] if len(location_parts) > 0 else ""
            state = location_parts[1] if len(location_parts) > 1 else ""
            country = location_parts[2] if len(location_parts) > 2 else ""
            
            # Get lat/lon for search location
            search_lat, search_lon = lookupLatLon(cityName=city, stateName=state, countryName=country)
            
            if search_lat != 0 or search_lon != 0:
                # Filter profiles by distance and store distance info
                profile_distances = {}
                filtered_profiles = []
                for profile in profiles:
                    if profile.lat and profile.lon:
                        try:
                            dist = haversine(search_lat, search_lon, float(profile.lat), float(profile.lon))
                            if dist <= distance_param:
                                filtered_profiles.append(profile.id)
                                profile_distances[profile.id] = round(dist, 1)
                        except (ValueError, TypeError):
                            pass
                
                if filtered_profiles:
                    profiles = profiles.filter(id__in=filtered_profiles)
                else:
                    # No profiles within distance, show empty results
                    profiles = profiles.none()
                
                # Attach distance to each profile
                for profile in profiles:
                    profile.distance = profile_distances.get(profile.id)

    # Work style filter
    work_style = data.get('work_style')
    if work_style and work_style != "":
        if isinstance(profiles, list):
            # If profiles is already a list, filter manually
            profiles = [p for p in profiles if p.work_style_preference == work_style or p.work_style_preference == ""]
        else:
            profiles = profiles.filter(Q(work_style_preference=work_style) | Q(work_style_preference=""))

    # Sorting - handle both QuerySet and list
    sort_by = data.get('sort_by') or 'recent'
    if isinstance(profiles, list):
        # Sort list manually
        if sort_by == 'name':
            profiles = sorted(profiles, key=lambda p: (p.user.first_name or '', p.user.last_name or '', p.user.username))
        elif sort_by == 'headline':
            profiles = sorted(profiles, key=lambda p: (p.headline or '', p.user.username))
        else:
            profiles = sorted(profiles, key=lambda p: p.user.date_joined, reverse=True)
    else:
        # Sort QuerySet
        if sort_by == 'name':
            profiles = profiles.order_by('user__first_name', 'user__last_name', 'user__username')
        elif sort_by == 'headline':
            profiles = profiles.order_by('headline', 'user__username')
        else:
            profiles = profiles.order_by('-user__date_joined')

    context = {
        'form': form,
        'profiles': profiles,
        'result_count': len(profiles) if isinstance(profiles, list) else profiles.count(),
        'active_skills': bubble_skills,
        'all_skills': all_skills,
        'skills_mode': skills_mode,
        'job': job,
        'recruiter_jobs': recruiter_jobs,
    }
    return render(request, 'home/candidate_search.html', context)
