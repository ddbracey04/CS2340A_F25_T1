from django.shortcuts import render

recruiters = [
    {
        'id': 1,
        'name': 'Recruiter 1',
        'description': 'Description for Recruiter 1',
        'price': 100
    },
    {
        'id': 2,
        'name': 'Recruiter 2',
        'description': 'Description for Recruiter 2',
        'price': 200
    },
    {
        'id': 3,
        'name': 'Recruiter 3',
        'description': 'Description for Recruiter 3',
        'price': 300
    },
]

def index(request):
    template_data = {}
    template_data['title'] = 'Recruiters'
    template_data['recruiters'] = recruiters
    return render(request, 'recruiters/index.html', {'template_data': template_data})

def show(request, id):
    recruiter = recruiters[id - 1]
    template_data = {}
    template_data['title'] = recruiter['name']
    template_data['recruiter'] = recruiter
    return render(request, 'recruiters/show.html' ,{'template_data': template_data})