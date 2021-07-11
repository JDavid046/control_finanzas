import datetime
import pandas as pd
import xlwt
import csv
from django.contrib.auth.models import User
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from xlwt.BIFFRecords import XcallSupBookRecord
from xlwt.Style import XFStyle
from sistema_control.models import Movimiento, Profile, TipoMovimiento
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import MovimientoForm, UserLoginForm, UserRegisterForm
from django.contrib.auth import get_user_model


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
def home(request):  
    ingresosUser = Movimiento.objects.filter(tipoMovimiento=1).aggregate(Sum('valorMovimiento'))
    ingresos = format(0,".3f") if ingresosUser['valorMovimiento__sum']==None else ingresosUser['valorMovimiento__sum']

    egresosUser = Movimiento.objects.filter(tipoMovimiento=2).aggregate(Sum('valorMovimiento'))
    egresos = format(0,".3f") if egresosUser['valorMovimiento__sum'] == None else egresosUser['valorMovimiento__sum']    

    context = {
        'ingresos':ingresos,
        'egresos':egresos
    }    
    return render(request, 'index.html', context)    

@login_required
def movimientos_usuario(request):
    
    if request.method != 'POST':
        movimientos = Movimiento.objects.filter(usuario = request.user)        
        movimientoForm = MovimientoForm()
        context = {'movimientos':movimientos, 'form':movimientoForm}        
    else:
        form = MovimientoForm(data=request.POST)

        if form.is_valid():

            user = request.user
            tipoNuevoMovimientoId = request.POST['tipoMovimiento']
            tipoNuevoMovimiento = TipoMovimiento.objects.get(id=tipoNuevoMovimientoId)
            
            descripcionNuevoMovimiento = request.POST['descripcionMovimiento']
            valorNuevoMovimiento = request.POST.get('valorMovimiento')

            diaNuevoMovimiento = request.POST['fechaMovimiento_day']
            mesNuevoMovimiento = request.POST['fechaMovimiento_month']
            anioNuevoMovimiento = request.POST['fechaMovimiento_year']

            fechaNuevoMovimiento = diaNuevoMovimiento+"/"+mesNuevoMovimiento+"/"+anioNuevoMovimiento
            fechaNuevoMovimiento = datetime.datetime.strptime(fechaNuevoMovimiento, "%d/%m/%Y").strftime("%Y-%m-%d")            
            
            Movimiento.objects.create(descripcionMovimiento=descripcionNuevoMovimiento,
                                        fechaMovimiento=fechaNuevoMovimiento, tipoMovimiento=tipoNuevoMovimiento,
                                        usuario=user, valorMovimiento=valorNuevoMovimiento)

            calculoNuevoCapital(request.user, int(valorNuevoMovimiento), tipoNuevoMovimiento.id)

            return HttpResponseRedirect(reverse('movimientos'))

    return render(request, 'movimientos.html', context)

def calculoNuevoCapital(usuario, valorMovimiento, tipoMovimiento):
    nuevoCapital = 0

    user = Profile.objects.get(user=usuario)     
    capital = user.capitalTotal

    if capital < valorMovimiento and tipoMovimiento == 2:
        user.deudas = capital - valorMovimiento
        user.capitalTotal = 0
        user.save()

    else:            
        if tipoMovimiento == 1:
            nuevoCapital = capital + valorMovimiento
        elif tipoMovimiento == 2:
            nuevoCapital = capital - valorMovimiento

        user.capitalTotal = nuevoCapital
        user.save()      

@login_required
def ingresos_usuario(request):
    movimientos = Movimiento.objects.all().filter(usuario = request.user, tipoMovimiento=1)           
    context = {'movimientos':movimientos}
    return render(request, 'ingresos.html', context)

@login_required
def egresos_usuario(request):
    movimientos = Movimiento.objects.all().filter(usuario = request.user, tipoMovimiento=2)           
    context = {'movimientos':movimientos}
    return render(request, 'egresos.html', context)    


def export_excel(request):    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Movimientos'+\
        str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='UTF-8')        
    ws = wb.add_sheet('Movimientos')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns =['ID', 'Tipo de Movimiento', 'Desripción del Movimiento', 'Valor del Movimiento', 'Fecha del movmiento']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Movimiento.objects.all().filter(usuario=request.user).values_list('id', 'tipoMovimiento', 'descripcionMovimiento', 'valorMovimiento', 'fechaMovimiento')    

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    return response