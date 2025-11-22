from urllib import request
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from map.utils import lookupLatLon
from users.models import CustomUser

from .forms import (
    CandidateSearchForm,
    EducationForm,
    ProfileForm,
    PrivacySettingsForm,
    ProfileHeadlineForm,
    ProfileLocationForm,
    ProfileCommuteRadiusForm,
    ProfileSkillsForm,
    ProfileWorkStyleForm,
    ProfileExperienceForm,
    ProfileLinksForm,
    SavedSearchForm,
)
from .models import Education, Profile, ProfilePrivacy, SavedSearch, Notification

from django.contrib import messages
from django.conf import settings

from .models import Message
from .forms import MessageForm
from django.views.decorators.http import require_GET


PROFILE_FIELD_FORM_CONFIG = {
    "headline": {
        "form_class": ProfileHeadlineForm,
        "prefix": "headline",
        "success_message": "Headline updated.",
    },
    "location": {
        "form_class": ProfileLocationForm,
        "prefix": "location",
        "success_message": "Location updated.",
    },
    "commute_radius": {
        "form_class": ProfileCommuteRadiusForm,
        "prefix": "commute_radius",
        "success_message": "Commute Radius updated.",
    },
    "skills": {
        "form_class": ProfileSkillsForm,
        "prefix": "skills",
        "success_message": "Skills updated.",
    },
    "work_style": {
        "form_class": ProfileWorkStyleForm,
        "prefix": "workstyle",
        "success_message": "Work style preference updated.",
    },
    "experience": {
        "form_class": ProfileExperienceForm,
        "prefix": "experience",
        "success_message": "Experience updated.",
    },
    "links": {
        "form_class": ProfileLinksForm,
        "prefix": "links",
        "success_message": "Links updated.",
    },
}


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
            profile.lat, profile.lon = lookupLatLon(streetAddr=profile.street_address, cityName=profile.city, stateName=profile.state, countryName=profile.country)
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


@login_required
@require_POST
def update_profile_field(request, username, field):
    user = get_object_or_404(CustomUser, username=username)
    if not (request.user == user or request.user.is_admin()):
        return HttpResponseForbidden()

    profile, _ = Profile.objects.get_or_create(user=user)
    config = PROFILE_FIELD_FORM_CONFIG.get(field)
    if not config:
        raise Http404()

    form = config["form_class"](request.POST, instance=profile, prefix=config["prefix"])

    if form.is_valid():
        profile = form.save(commit=False)
        location_changed = field == "location" and form.has_changed()
        profile.save()

        if location_changed:
            if profile.street_address or profile.city or profile.state or profile.country:
                try:
                    profile.lat, profile.lon = lookupLatLon(streetAddr=profile.street_address, cityName=profile.city, stateName=profile.state, countryName=profile.country)
                except Exception:
                    profile.lat, profile.lon = (0, 0)
            else:
                profile.lat, profile.lon = (0, 0)
            profile.save(update_fields=['lat', 'lon'])

        messages.success(request, config["success_message"])
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    return redirect('profile.view', username=username)


def profile_view(request, username):
    from django.contrib.auth import get_user_model

    CustomUser = get_user_model()
    user = get_object_or_404(CustomUser, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    ProfilePrivacy.objects.get_or_create(profile=profile)
    user_education = Education.objects.filter(user=user).order_by('pk')

    if profile.privacy and profile.privacy.is_profile_visible == False and request.user.is_recruiter():
        return redirect(request.META.get("HTTP_REFERER"))

    forms_context = {}
    education_form = None
    if request.user.is_authenticated and (request.user == user or request.user.is_admin()):
        forms_context = {
            'headline_form': PROFILE_FIELD_FORM_CONFIG['headline']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['headline']["prefix"]),
            'location_form': PROFILE_FIELD_FORM_CONFIG['location']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['location']["prefix"]),
            'commute_radius_form': PROFILE_FIELD_FORM_CONFIG['commute_radius']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['commute_radius']["prefix"]),
            'skills_form': PROFILE_FIELD_FORM_CONFIG['skills']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['skills']["prefix"]),
            'work_style_form': PROFILE_FIELD_FORM_CONFIG['work_style']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['work_style']["prefix"]),
            'experience_form': PROFILE_FIELD_FORM_CONFIG['experience']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['experience']["prefix"]),
            'links_form': PROFILE_FIELD_FORM_CONFIG['links']["form_class"](instance=profile, prefix=PROFILE_FIELD_FORM_CONFIG['links']["prefix"]),
        }
        education_form = EducationForm()

    return render(request, 'home/profile_view.html', {
        'profile': profile,
        'owner': user,
        'user_education': user_education,
        'forms': forms_context,
        'education_form': education_form,
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
        # Get jobs and manually count applications for each
        jobs = Job.objects.filter(users=request.user).order_by('-date')
        recruiter_jobs = []
        for job_item in jobs:
            # Count applications for this job directly from the database
            job_item.applicant_count = Application.objects.filter(job=job_item).count()
            recruiter_jobs.append(job_item)
    
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

    profiles = Profile.objects.select_related('user').filter(Q(user__role=CustomUser.Role.JOB_SEEKER) & Q(privacy__is_profile_visible=True))
    
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
            profiles = profiles.filter((Q(work_style_preference=work_style) | Q(work_style_preference="")) & Q(privacy__show_work_style_preference=True))

    # Sorting - handle both QuerySet and list
    sort_by = data.get('sort_by') or 'recent'
    if isinstance(profiles, list):
        # Sort list manually
        if sort_by == 'name':
            profiles = sorted(profiles, key=lambda p: (p.user.first_name or '', p.user.last_name or '', p.user.username))
        elif sort_by == 'headline':
            profiles = sorted(profiles, key=lambda p: (p.headline or '', p.user.username))
        else: # 'recent'
            # Assuming user objects have a date_joined attribute
            profiles = sorted(profiles, key=lambda p: p.user.date_joined, reverse=True)
    else:
        # Sort QuerySet
        if sort_by == 'name':
            profiles = profiles.order_by('user__first_name', 'user__last_name', 'user__username')
        elif sort_by == 'headline':
            profiles = profiles.order_by('headline', 'user__username')
        else: # 'recent'
            profiles = profiles.order_by('-user__date_joined')

    saved_search_form = SavedSearchForm()
    total_profiles_count = Profile.objects.filter(user__role=CustomUser.Role.JOB_SEEKER).count()

    if request.method == 'POST' and 'save_search' in request.POST:
        if not request.user.is_authenticated or not request.user.is_recruiter():
            return redirect('users.login')

        post_data = request.POST.copy()
        post_data.update({
            'experience': data.get('experience', ''),
            'skills': ','.join(bubble_skills),
            'skills_mode': request.GET.get('skills_mode', 'OR'),
            'location': data.get('location', ''),
            'distance': distance_param,
            'work_style': data.get('work_style', ''),
        })
        
        form = SavedSearchForm(post_data)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.recruiter = request.user
            saved_search.save()
            messages.success(request, f"Search '{saved_search.name}' saved successfully!")
            return redirect(request.get_full_path())
        else:
            # If form is invalid, it's likely a duplicate name or other validation error.
            # We can pass the form with errors back to the template.
            saved_search_form = form


    context = {
        'form': form,
        'profiles': profiles,
        'result_count': len(profiles) if isinstance(profiles, list) else profiles.count(),
        'active_skills': bubble_skills,
        'all_skills': all_skills,
        'skills_mode': skills_mode,
        'job': job,
        'recruiter_jobs': recruiter_jobs,
        'selected_job_id': int(job_id) if job_id else None,
        'total_profiles': total_profiles_count,
        'saved_search_form': saved_search_form,
        'current_filters': {
            'experience': experience,
            'skills': ','.join(bubble_skills),
            'skills_mode': skills_mode,
            'location': data.get('location'),
            'distance': distance_param,
            'work_style': work_style,
        }
    }
    return render(request, 'home/candidate_search.html', context)

@login_required
def privacy_settings(request):
    if not request.user.is_job_seeker():
        messages.error(request, "Only job seekers can access privacy settings.")
        return redirect('home')
    
    # get or create privacy settings
    privacy, created = ProfilePrivacy.objects.get_or_create(profile=request.user.home_profile)
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=privacy)
        if form.is_valid():
            form.save()
            messages.success(request, "Privacy settings updated successfully!")
            return redirect('privacy_settings')
    else:
        form = PrivacySettingsForm(instance=privacy)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'home/privacy_settings.html', context)

@login_required
def saved_searches(request):
    if not request.user.is_recruiter():
        return HttpResponseForbidden()
    
    searches = SavedSearch.objects.filter(recruiter=request.user)
    
    context = {
        'saved_searches': searches
    }
    return render(request, 'home/saved_searches.html', context)

@login_required
@require_POST
def delete_saved_search(request, search_id):
    if not request.user.is_recruiter():
        return HttpResponseForbidden()
    
    search = get_object_or_404(SavedSearch, id=search_id, recruiter=request.user)
    search.delete()
    messages.success(request, "Saved search deleted successfully.")
    return redirect('saved_searches')


@login_required
def notifications(request):
    if not request.user.is_recruiter():
        return HttpResponseForbidden()
    
    user_notifications = Notification.objects.filter(recipient=request.user)
    unread_count = user_notifications.filter(is_read=False).count()
    
    context = {
        'notifications': user_notifications,
        'unread_count': unread_count
    }
    return render(request, 'home/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    if not request.user.is_recruiter():
        return HttpResponseForbidden()
    
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


@login_required
@require_POST
def mark_all_notifications_read(request):
    if not request.user.is_recruiter():
        return HttpResponseForbidden()
    
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications')


@login_required
def message_compiler(request):
    # Only recruiter or admin may send messages
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username'].strip()
            job_id = form.cleaned_data.get('job_id')
            message_text = form.cleaned_data['message_text']
            send_method = form.cleaned_data.get('send_method')
            send_in_app = True if send_method == 'in_app' else False

            # Resolve recipient
            recipient = get_object_or_404(CustomUser, username=recipient_username)

            # Resolve optional job
            job = None
            if job_id:
                try:
                    from jobs.models import Job
                    job = Job.objects.filter(pk=job_id).first()
                except Exception:
                    job = None

            # Create message instance
            message_obj = Message.objects.create(
                job=job,
                sender=request.user,
                recipient=recipient,
                text=message_text,
                in_app=send_in_app,
            )

            # If email option selected, send actual email
            if not send_in_app:
                from django.core.mail import send_mail

                subject = f"Message from {request.user.get_full_name() or request.user.username}"
                if job:
                    subject += f" regarding {job.title}"

                email_body = f"""Hello {recipient.get_full_name() or recipient.username},

You have received a message from {request.user.get_full_name() or request.user.username}:

{message_text}

---
This message was sent via Early Career Jobs platform.
"""

                try:
                    send_mail(
                        subject=subject,
                        message=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    messages.success(request, 'Email sent successfully!')
                except Exception as e:
                    messages.error(request, f'Message saved but email failed to send: {str(e)}')
                    return redirect('home.message_compiler')

            messages.success(request, 'Message Sent.')
            return redirect('home.message_compiler')
    else:
        recipient_prefill = request.GET.get('recipient', '')
        job_prefill = request.GET.get('job_id', '')
        initial = {}
        if recipient_prefill:
            initial['recipient_username'] = recipient_prefill
        if job_prefill:
            initial['job_id'] = job_prefill
        form = MessageForm(initial=initial)

    return render(request, 'home/message_compiler.html', {'form': form})


@login_required
@require_GET
def search_usernames(request):
    """Return JSON list of job seeker usernames matching query 'q'.

    Accessible only to recruiters or admins.
    """
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return JsonResponse({'results': []}, status=403)

    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    # Match usernames (case-insensitive startswith), limit results
    matches = CustomUser.objects.filter(username__istartswith=q, role=CustomUser.Role.JOB_SEEKER).order_by('username')[:20]
    return JsonResponse({'results': [u.username for u in matches]})

@login_required
def inbox(request):
    # Display inbox for job seekers to view messages sent to them.
    if not request.user.is_job_seeker():
        return HttpResponseForbidden("Only job seekers can access the inbox.")
    
    # Get all messages where current user is the recipient
    messages_list = Message.objects.filter(recipient=request.user).select_related('sender', 'job').order_by('-created_at')
    
    # Count unread messages
    unread_count = messages_list.filter(is_read=False).count()
    
    context = {
        'messages_list': messages_list,
        'unread_count': unread_count,
    }
    return render(request, 'home/inbox.html', context)


@login_required
@require_POST
def mark_message_read(request, message_id):
    # Mark a specific message as read.
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.is_read = True
    message.save()
    return redirect('home.inbox')