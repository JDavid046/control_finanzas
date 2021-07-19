import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import numpy as np
from django.contrib.auth.forms import UserCreationForm
from numpy.random.mtrand import randint
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
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import MovimientoForm, UserLoginForm, UserRegisterForm
from django.contrib.auth import get_user_model
from django.db.models.functions import Extract


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
            return HttpResponseRedirect(reverse('home'))

    context = {'form': form}
    return render(request, 'register.html', context)            


def olvide_contrasena(request):    
    context = {'mensaje':''}
    try:
        if request.method == 'POST':
            correo = request.POST['inputEmail']
            usuario = User.objects.get(email=correo)
            nuevaContrasena = crear_random_contrasena()
            contrasena_hashed = make_password(nuevaContrasena)            
            usuario.password = contrasena_hashed
            usuario.save()

            enviar_correo(nuevaContrasena, correo)

            context = {'mensaje':'Se ha enviado un correo. Por favor revisar e Iniciar Sesión.'}
    except:
        context = {'mensaje':'No existe el Usuario con el correo proporcionado.'}
        
    return render(request, 'password.html', context)


def crear_random_contrasena():

    contrasena_generada = ""

    minusculas = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    mayusculas = [x.upper() for x in minusculas]
    numeros = [x for x in range(0,10)]
    especiales = ['+', '-', '*', '#']

    for x in range(0,3):
        rand_minus = np.random.randint(len(minusculas))
        rand_mayus = np.random.randint(len(mayusculas))
        rand_num = np.random.randint(len(numeros))
        rand_espe = np.random.randint(len(especiales))

        contrasena_generada += minusculas[rand_minus] + mayusculas[rand_mayus] + str(numeros[rand_num]) + especiales[rand_espe]

    return contrasena_generada


def enviar_correo(mensaje, correo):
    # create message object instance
    msg = MIMEMultipart()
    
    message = "Mis Finanzas App\n\nHola. Has pedido una nueva contraseña.\n\nTu nueva contraseña es: "+ mensaje + "\n\nSi no has pedido un cambio comunicate con administración.\nGracias."
    
    # setup the parameters of the message
    password = "MaestroYagger46*"
    msg['From'] = "mfinanzasapp@gmail.com"
    msg['To'] = correo
    msg['Subject'] = "MisFinanzasApp: Cambio de Contraseña"
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    server.starttls()
    
    # Login Credentials for sending the mail
    server.login(msg['From'], password)
    
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()



@login_required
def home(request):  
    ingresosUser = Movimiento.objects.filter(usuario=request.user,tipoMovimiento=1).aggregate(Sum('valorMovimiento'))
    ingresos = format(0,".3f") if ingresosUser['valorMovimiento__sum']==None else ingresosUser['valorMovimiento__sum']

    egresosUser = Movimiento.objects.filter(usuario=request.user,tipoMovimiento=2).aggregate(Sum('valorMovimiento'))
    egresos = format(0,".3f") if egresosUser['valorMovimiento__sum'] == None else egresosUser['valorMovimiento__sum']


    # Cálculo de ingresos por Mes
    ingresos_por_mes_query = Movimiento.objects.filter(usuario=request.user,tipoMovimiento=1).annotate(totalIngresos=Sum('valorMovimiento'),month=Extract('fechaMovimiento', 'month')).values('totalIngresos', 'month').order_by('month')
    ingresos_por_mes = [0 for x in range(1,13)]    
    
    for x in range(len(ingresos_por_mes_query)):
        objeto = ingresos_por_mes[ingresos_por_mes_query[x]['month']-1]    
        if objeto != 0:
            ingresos_por_mes[ingresos_por_mes_query[x]['month']-1] = objeto + float(ingresos_por_mes_query[x]['totalIngresos'])
        else:
            ingresos_por_mes[ingresos_por_mes_query[x]['month']-1] = float(ingresos_por_mes_query[x]['totalIngresos'])


    # Cálculo de Egresos por mes
    egresos_por_mes_query = Movimiento.objects.filter(usuario=request.user,tipoMovimiento=2).annotate(totalIngresos=Sum('valorMovimiento'),month=Extract('fechaMovimiento', 'month')).values('totalIngresos', 'month').order_by('month')
    egresos_por_mes = [0 for x in range(1,13)]    
    
    for x in range(len(egresos_por_mes_query)):
        objeto = egresos_por_mes[egresos_por_mes_query[x]['month']-1]    
        if objeto != 0:
            egresos_por_mes[egresos_por_mes_query[x]['month']-1] = objeto + float(egresos_por_mes_query[x]['totalIngresos'])
        else:
            egresos_por_mes[egresos_por_mes_query[x]['month']-1] = float(egresos_por_mes_query[x]['totalIngresos'])

    context = {
        'ingresos':ingresos,
        'egresos':egresos,
        'ingresos_por_mes':ingresos_por_mes,
        'egresos_por_mes':egresos_por_mes,
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

            calculo = calculoNuevoCapital(request.user, int(valorNuevoMovimiento), tipoNuevoMovimiento.id, 'nuevo', None)
            if calculo:
                Movimiento.objects.create(descripcionMovimiento=descripcionNuevoMovimiento,
                                        fechaMovimiento=fechaNuevoMovimiento, tipoMovimiento=tipoNuevoMovimiento,
                                        usuario=user, valorMovimiento=valorNuevoMovimiento)

                return HttpResponseRedirect(reverse('movimientos'))
            else:
                movimientos = Movimiento.objects.filter(usuario = request.user)        
                movimientoForm = MovimientoForm()
                context = {'movimientos':movimientos, 'form':movimientoForm, 'errores': True}                                      

    return render(request, 'movimientos.html', context)

def calculoNuevoCapital(usuario, valorMovimiento, tipoMovimiento, accion, valorAnterior):
    estatus = False
    nuevoCapital = 0

    user = Profile.objects.get(user=usuario)     
    capital = user.capitalTotal

    if accion == 'nuevo':        
        if capital < valorMovimiento and tipoMovimiento == 2:            
            estatus = False

        else:            
            if tipoMovimiento == 1:
                nuevoCapital = capital + valorMovimiento
            elif tipoMovimiento == 2:
                nuevoCapital = capital - valorMovimiento

            user.capitalTotal = nuevoCapital
            user.save()

            estatus = True 

    elif accion == 'editar':        

        if capital < valorMovimiento and tipoMovimiento == 2:
            estatus = False

        else:
            if tipoMovimiento == 2:
                if valorMovimiento > valorAnterior:
                    nuevoCapital = capital - (valorMovimiento - valorAnterior)
                elif valorMovimiento < valorAnterior:
                    nuevoCapital = capital + (valorAnterior -valorMovimiento)
                else:
                    nuevoCapital = capital
            else:
                if valorMovimiento > valorAnterior:
                    nuevoCapital = capital + (valorMovimiento - valorAnterior)
                elif valorMovimiento < valorAnterior:
                    nuevoCapital = capital - (valorAnterior -valorMovimiento)
                else:
                    nuevoCapital = capital                    

            user.capitalTotal = nuevoCapital
            user.save()

            estatus = True

    return estatus            


@login_required
def editar_movimiento(request, id):
    movimiento = Movimiento.objects.get(id = id)
    valorAnterior = movimiento.valorMovimiento    
    if request.method != 'POST':
        form = MovimientoForm(instance=movimiento)
        contexto = {'form':form}
    else:
        form = MovimientoForm(request.POST, instance=movimiento)
        contexto = {'form':form}

        if form.is_valid():           

            tipoNuevoMovimientoId = request.POST['tipoMovimiento']
            tipoMovimiento = TipoMovimiento.objects.get(id=tipoNuevoMovimientoId)
            valorMovimiento = request.POST.get('valorMovimiento')                                    

            calculo = calculoNuevoCapital(request.user, int(float(valorMovimiento)), tipoMovimiento.id, 'editar', valorAnterior)                
            if calculo:
                form.save()
                return HttpResponseRedirect(reverse('movimientos'))
            else:                
                form = MovimientoForm(instance=movimiento)
                contexto = {'form':form, 'errores':True}
    return render(request, 'editarMovimiento.html', contexto)            


@login_required
def eliminar_movimiento(request, id):
    movimiento = Movimiento.objects.get(id=id)
    usuario = Profile.objects.get(user=request.user)    
    
    if movimiento.tipoMovimiento_id == 1:
        usuario.capitalTotal = usuario.capitalTotal - movimiento.valorMovimiento
        usuario.save()

        movimiento.delete()

    elif movimiento.tipoMovimiento_id == 2:
        usuario.capitalTotal = usuario.capitalTotal + movimiento.valorMovimiento
        usuario.save()

        movimiento.delete()

    return redirect('movimientos')

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


def export_excel(request, nombre):    
    response = HttpResponse(content_type='application/ms-excel')    

    response['Content-Disposition'] = 'attachment; filename="'+nombre+' de "'+request.user.username+" "+\
        str(datetime.datetime.now()) + '.xls'    

    wb = xlwt.Workbook(encoding='UTF-8')        
    ws = wb.add_sheet(nombre)
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns =['ID', 'Tipo de Movimiento', 'Desripción del Movimiento', 'Valor del Movimiento', 'Fecha del movimiento']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    switch_tabla = {        
        'movimiento':Movimiento.objects.all().filter(usuario=request.user).values_list('id', 'tipoMovimiento', 'descripcionMovimiento', 'valorMovimiento', 'fechaMovimiento'),
        'ingreso':Movimiento.objects.all().filter(usuario=request.user,tipoMovimiento=1).values_list('id', 'tipoMovimiento', 'descripcionMovimiento', 'valorMovimiento', 'fechaMovimiento'),
        'egreso':Movimiento.objects.all().filter(usuario=request.user,tipoMovimiento=2).values_list('id', 'tipoMovimiento', 'descripcionMovimiento', 'valorMovimiento', 'fechaMovimiento'),
    }

    rows = None

    if nombre == 'Movimientos':
        rows = switch_tabla['movimiento']
    elif nombre == 'Ingresos':
        rows = switch_tabla['ingreso']
    elif nombre == 'Egresos':
        rows = switch_tabla['egreso']        

         
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    wb.save(response)

    return response

@login_required
def  perfil_usuario(request):
    if request.method == 'POST':
        name = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        correo = request.POST.get('correo')

        usuario = User.objects.get(id=request.user.id)
        usuario.first_name = name
        usuario.last_name = apellido
        usuario.username = username
        usuario.email = correo

        usuario.save()
        return HttpResponseRedirect(reverse('perfil'))

    else:
        context = {'error':''}        

    return render(request, 'perfil.html', context)


@login_required
def cambiar_contrasena(request):
    usuario = User.objects.get(id=request.user.id)
    contrasenaActual = request.POST['contrasenaActual']
    contrasenaNueva = request.POST['contrasenaNueva']        
    regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$|^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$|^(?=.*[a-z])(?=.*[A-Z])[a-zA-Z\d]{8,}$|^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    
    if check_password(contrasenaActual, usuario.password):        
        if re.search(regex, contrasenaNueva):

            usuario.password = make_password(contrasenaNueva)
            usuario.save()

            return HttpResponseRedirect(reverse('logout'))
        else:
            context = {'error':'Ingrese una contraseña válida.'}

    else:
        context = {'error':'La Contraseña Actual es incorrecta.'}
    
    return render(request, 'perfil.html', context)