from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render,get_object_or_404
from .models import Profile, Education
from .forms import ProfileForm, EducationForm
from django.contrib.auth import login
from django.http import JsonResponse

from map.utils import lookupLatLon


def index(request):
    return render(request, "home/index.html")


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})


#adding for profile
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
    #return render(request, 'home/profile_form.html', {'form': form})

    education_form = EducationForm()
    user_education = Education.objects.filter(user=request.user).order_by('pk')

    return render(request, 'home/profile_form.html', {
        'form': form,
        'education_form': education_form,
        'user_education': user_education,
    })
@login_required
def save_education(request, education_id = None):
    if request.method == 'POST':
        instance = None
        if education_id:
            try:
                instance = Education.objects.get(pk=education_id, user=request.user)
            except Education.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Education entry not found.'}, status=404)
        form = EducationForm(request.POST, instance = instance)

        if form.is_valid():
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
                'form_data': form.cleaned_data
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status = 400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def profile_view(request, username):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    #return render(request, 'home/profile_view.html', {'profile': profile, 'owner': user})
    user_education = Education.objects.filter(user=user).order_by('pk')
    return render(request, 'home/profile_view.html', {'profile': profile, 'owner': user, 'user_education': user_education})

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