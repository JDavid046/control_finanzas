from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import *
from .forms import *

@login_required
def home(request):    
    return render(request, 'index.html')

def register(request):
    if request.method =='POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            messages.success(request, 'Usuario: ' + username + ' creado.\n Inicie Sesión')
            return redirect('login')
    else:
        form = UserRegisterForm()

    context = {'form':form}                
    return render(request, 'register.html', context)

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        email = request.POST["email"]
        password = request.POST["password"]
        print(email)
        print(password)
        user = authenticate(email=email, password=password)
        print(user)
        if user:            
            login(request, user)
            return render(request, 'index.html')

    else:        
        form = UserLoginForm()

    context = {'form':form}                
    return render(request, 'login.html', context)