from django.shortcuts import render

from .forms import JobSearchForm
from .models import Job


def index(request):
    form = JobSearchForm(request.GET or None)
    jobs = Job.objects.all()

    if form.is_valid():
        data = form.cleaned_data

        if data.get("title"):
            jobs = jobs.filter(title__icontains=data["title"])

        if data.get("skills"):
            skill_terms = [term.strip() for term in data["skills"].split(",") if term.strip()]
            for term in skill_terms:
                jobs = jobs.filter(skills__icontains=term)

        if data.get("city"):
            jobs = jobs.filter(city__iexact=data["city"])

        if data.get("state"):
            jobs = jobs.filter(state__iexact=data["state"])

        if data.get("country"):
            jobs = jobs.filter(country__iexact=data["country"])

        if data.get("salary_min") is not None:
            jobs = jobs.filter(salary_min__gte=data["salary_min"])

        if data.get("salary_max") is not None:
            jobs = jobs.filter(salary_max__lte=data["salary_max"])

        if data.get("work_style"):
            jobs = jobs.filter(work_style=data["work_style"])

        if data.get("visa_sponsorship"):
            jobs = jobs.filter(visa_sponsorship=True)

    template_data = {"title": "Job Search"}

    context = {
        "template_data": template_data,
        "form": form,
        "jobs": jobs,
    }

    return render(request, "home/index.html", context)


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})
