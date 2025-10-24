from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from map.utils import lookupLatLon
from users.models import CustomUser

from .forms import CandidateSearchForm, EducationForm, ProfileForm, PrivacySettingsForm
from .models import Education, Profile, ProfilePrivacy

from django.contrib import messages


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

    CustomUser = get_user_model()
    user = get_object_or_404(CustomUser, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    user_education = Education.objects.filter(user=user).order_by('pk')

    if user.home_profile.privacy.is_profile_visible == False and request.user.is_recruiter():
        return redirect(request.META.get("HTTP_REFERER"))

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
    if form.is_valid():
        data = form.cleaned_data
    else:
        data = {
            'keywords': '',
            'work_style': '',
            'sort_by': CandidateSearchForm.SORT_CHOICES[0][0],
        }
        form = CandidateSearchForm(initial=data)

    profiles = Profile.objects.select_related('user').filter(Q(user__role=CustomUser.Role.JOB_SEEKER) & Q(privacy__is_profile_visible=True))

    keywords = data.get('keywords')
    if keywords:
        profiles = profiles.filter(
            Q(user__first_name__icontains=keywords) |
            Q(user__last_name__icontains=keywords) |
            Q(user__username__icontains=keywords) |
            Q(headline__icontains=keywords) |
            Q(skills__icontains=keywords) |
            Q(experience__icontains=keywords) |
            Q(user__educations__degree__icontains=keywords) |
            Q(user__educations__institution__icontains=keywords)
        ).distinct()

    work_style = data.get('work_style')
    if work_style and work_style != "":
        profiles = profiles.filter((Q(work_style_preference=work_style) | Q(work_style_preference="")) & Q(privacy__show_work_style_preference=True))

    sort_by = data.get('sort_by') or 'recent'
    if sort_by == 'name':
        profiles = profiles.order_by('user__first_name', 'user__last_name', 'user__username')
    elif sort_by == 'headline':
        profiles = profiles.order_by('headline', 'user__username')
    else:
        profiles = profiles.order_by('-user__date_joined')

    context = {
        'form': form,
        'profiles': profiles,
        'result_count': profiles.count(),
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