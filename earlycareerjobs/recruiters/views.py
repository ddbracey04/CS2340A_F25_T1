from django.shortcuts import render, redirect
from .models import Recruiter, Application
from django.contrib.auth.decorators import login_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        recruiters = Recruiter.objects.filter(name__icontains=search_term)
    else:
        recruiters = Recruiter.objects.all()
    template_data = {}
    template_data['title'] = 'Recruiters'
    template_data['recruiters'] = recruiters
    return render(request, 'recruiters/index.html', {'template_data': template_data})

def show(request, id):
    recruiter = Recruiter.objects.get(id=id)
    template_data = {}
    template_data['title'] = recruiter.name
    template_data['recruiter'] = recruiter
    # Determine whether the current user has already applied to this recruiter
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(recruiter=recruiter, user=request.user).exists()
    template_data['has_applied'] = has_applied
    return render(request, 'recruiters/show.html', {'template_data': template_data})

@login_required
def start_application(request, id):
    if request.method == 'POST': #and request.POST['note'] != '' shouldnt be necessary to require user to input a personal note if they don't want to
        recruiter = Recruiter.objects.get(id=id)
        application = Application()
        application.user_note = request.POST['user_note']
        application.recruiter = recruiter
        application.user = request.user
        application.save()
        return redirect('recruiters.show', id=id)
    else:
        return redirect('recruiters.show', id=id)