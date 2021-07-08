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
