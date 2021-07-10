from django.db.models.aggregates import Sum
from sistema_control.models import Movimiento, Profile, TipoMovimiento
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth import get_user_model

@login_required
def home(request):  
    ingresos = Movimiento.objects.filter(tipoMovimiento=1).aggregate(Sum('valorMovimiento'))
    egresos = Movimiento.objects.filter(tipoMovimiento=2).aggregate(Sum('valorMovimiento'))
    context = {
        'ingresos':ingresos['valorMovimiento__sum'],
        'egresos':egresos['valorMovimiento__sum']
    }    
    return render(request, 'index.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

def user_login(request):
    if request.method != 'POST':
        form = UserLoginForm()

    else:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        print(user)
        print(username)
        print(password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            form = UserLoginForm()
            context = {'form':form, 'login_wrong':True}
            return render(request, 'login.html', context)

    context = {'form':form}
    return render(request, 'login.html', context)


def user_register(request):
    if request.method != 'POST':
        form = UserRegisterForm()

    else:
        form = UserRegisterForm(data=request.POST)

        if form.is_valid():

            username = request.POST['username']  
            email = request.POST['email']                                   
            password = request.POST['password1']
            User = get_user_model()
            User.objects.create_user(username=username, email=email,password=password)
            authenticated_user = authenticate(username=username, email=email,password=password)
            login(request, authenticated_user)
            #form.save()
            return HttpResponseRedirect(reverse('home'))

    context = {'form': form}
    return render(request, 'register.html', context)            


def olvide_contrasena(request):
    return render(request, 'password.html')

@login_required
def movimientos_usuario(request):
    movimientos = Movimiento.objects.filter(usuario = request.user)
    context = {'movimientos':movimientos}    
    return render(request, 'movimientos.html', context)