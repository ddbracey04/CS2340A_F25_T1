from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate

from .forms import RegForm
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
# def login(request):
#     template_data = {}
#     template_data['titlle'] = 'Login'
#     if request.method == 'GET':
#         return render(request, 'accounts/login.html', {'template_data': template_data})
#     if request.method == 'POST':
#         user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        
#         if user is None:
#             template_data['error'] = 'Username or password is incorrect'
#             return render(request, 'accounts/login.html', {'template_data': template_data})
        
#         else:
#             auth_login(request, user)
#             return render('home.index')



def register(request):
    template_data = {}
    template_data['titlle'] = 'Register'
    if request.method == 'GET':
        template_data['form'] = UserCreationForm()
        return render(request, 'accounts/register.html', {'template_data': template_data})
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home.index')
        else:
            template_data['form'] = form
            return render(request, 'accounts/register.html', {'template_data': template_data})
    

# if request.method == 'POST':
#         form = RegForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)

#             #later add feature to send message of success
#             return redirect('index')

#         pass
#         #later add feature to send message of failure
#     else:
#         form = RegForm()
#     return render(request, 'accounts/register.html', {'form': form})