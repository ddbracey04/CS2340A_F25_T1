from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render,get_object_or_404
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth import login

# Create your views here.
def index(request):
    return render(request, 'home/index.html')

######adding
@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile.detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'home/profile_form.html', {'form': form})

def profile_detail(request, username):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    return render(request, 'home/profile_detail.html', {'profile': profile, 'owner': user})