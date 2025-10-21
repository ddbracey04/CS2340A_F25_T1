from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from users.models import CustomUser

from .forms import CandidateSearchForm, ProfileForm
from .models import Profile


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
            return redirect('profile.view', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'home/profile_form.html', {'form': form})

def profile_view(request, username):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    return render(request, 'home/profile_view.html', {'profile': profile, 'owner': user})


@login_required
def search_candidates(request):
    if not (request.user.is_recruiter() or request.user.is_admin()):
        return HttpResponseForbidden()

    form = CandidateSearchForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
    else:
        data = {'keywords': '', 'work_style': '', 'sort_by': CandidateSearchForm.SORT_CHOICES[0][0]}
        form = CandidateSearchForm(initial=data)

    profiles = Profile.objects.select_related('user').filter(user__role=CustomUser.Role.JOB_SEEKER)

    keywords = data.get('keywords')
    if keywords:
        profiles = profiles.filter(
            Q(user__first_name__icontains=keywords) |
            Q(user__last_name__icontains=keywords) |
            Q(user__username__icontains=keywords) |
            Q(headline__icontains=keywords) |
            Q(skills__icontains=keywords) |
            Q(experience__icontains=keywords) |
            Q(education__icontains=keywords)
        )

    work_style = data.get('work_style')
    if work_style:
        profiles = profiles.filter(work_style_preference=work_style)

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
