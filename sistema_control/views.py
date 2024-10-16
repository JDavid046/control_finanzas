import datetime
from datetime import date
import re
from .excel import excel
from django.conf import settings
from django.db.models import query
import numpy as np
from django.contrib.auth.forms import UserCreationForm
from numpy.random.mtrand import randint
from django.contrib.auth.models import User
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from xlwt.BIFFRecords import XcallSupBookRecord
from xlwt.Style import XFStyle
from sistema_control.models import Movimiento, Profile, Programador, TipoMovimiento, Categorias
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import MovimientoForm, ProgramadorForm, UserLoginForm, UserRegisterForm, EditarMovimientoForm, CategoriasForm
from django.contrib.auth import get_user_model
from django.db.models.functions import Extract
from django.db import connection
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .calculoMovimientos import *


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def user_login(request):
    if request.method != "POST":
        form = UserLoginForm()

    else:
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            form = UserLoginForm()
            context = {"form": form, "login_wrong": True}
            return render(request, "login.html", context)

    context = {"form": form}
    return render(request, "login.html", context)


def user_register(request):
    if request.method != "POST":
        form = UserRegisterForm()

    else:
        form = UserRegisterForm(data=request.POST)

        if form.is_valid():

            username = request.POST["username"]
            email = request.POST["email"]
            password = request.POST["password1"]
            User = get_user_model()
            User.objects.create_user(username=username, email=email, password=password)
            authenticated_user = authenticate(
                username=username, email=email, password=password
            )
            login(request, authenticated_user)
            return HttpResponseRedirect(reverse("home"))

    context = {"form": form}
    return render(request, "register.html", context)


def olvide_credenciales(request, accion):
    if accion == "password":
        context = {
            "mensaje": "",
            "titulo": "Recuperar Contraseña",
            "descripcion": "la contraseña.",
        }
    else:
        context = {
            "mensaje": "",
            "titulo": "Recuperar Usuario",
            "descripcion": "el usuario.",
        }
    try:
        if request.method == "POST":
            correo = request.POST["inputEmail"]
            usuario = User.objects.get(email__contains=correo)

            if accion == "password":
                nuevaContrasena = crear_random_contrasena()
                contrasena_hashed = make_password(nuevaContrasena)
                usuario.password = contrasena_hashed
                usuario.save()

                params = {
                    "subject": "Cambio de Contraseña",
                    "mensaje": "un cambio de contraseña.",
                    "mensaje2": "Tu nueva contraseña es: ",
                    "mensaje3": nuevaContrasena,
                    "advertencia": "Si no has pedido un cambio de contraseña, contacta con el administrador."
                }

                enviar_correo(params, correo)

            else:
                params = {
                    "subject": "Recuperación Usuario",
                    "mensaje": "recordar tu Usuario.",
                    "mensaje2": "Tu Usuario es: ",
                    "mensaje3": usuario.username,                    
                    "advertencia": "Si no has pedido recordar el Usuario, contacta con el administrador." 
                }

                enviar_correo(params, correo)

            context = {
                "mensaje": "Se ha enviado un correo. Por favor revisar e Iniciar Sesión."
            }
    except:
        context = {"mensaje": "No existe el Usuario con el correo proporcionado."}

    return render(request, "credentials.html", context)


def crear_random_contrasena():

    contrasena_generada = ""

    minusculas = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    mayusculas = [x.upper() for x in minusculas]
    numeros = [x for x in range(0, 10)]
    especiales = ["+", "-", "*", "#"]

    for x in range(0, 3):
        rand_minus = np.random.randint(len(minusculas))
        rand_mayus = np.random.randint(len(mayusculas))
        rand_num = np.random.randint(len(numeros))
        rand_espe = np.random.randint(len(especiales))

        contrasena_generada += (
            minusculas[rand_minus]
            + mayusculas[rand_mayus]
            + str(numeros[rand_num])
            + especiales[rand_espe]
        )

    return contrasena_generada


def enviar_correo(mensaje, correo):
        
    subject = mensaje["subject"]
    receiver_email = correo    

    template = render_to_string('email_template.html',{
        'mensaje': mensaje["mensaje"],
        'mensaje2': mensaje["mensaje2"],
        'mensaje3': mensaje["mensaje3"],
        'advertencia': mensaje["advertencia"]
    })
    
    email = EmailMessage(
        subject,
        template,
        settings.EMAIL_HOST_USER,
        [receiver_email]
    )

    email.content_subtype = "html"
    email.fail_silently = False
    email.send()        


@login_required
def home(request):
    if request.method != "POST":
        ingresosUser = Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=1, fechaMovimiento__contains=datetime.date.today().year
        ).aggregate(Sum("valorMovimiento"))
        ingresos = (
            format(0, ".3f")
            if ingresosUser["valorMovimiento__sum"] == None
            else ingresosUser["valorMovimiento__sum"]
        )

        egresosUser = Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=2, fechaMovimiento__contains=datetime.date.today().year
        ).aggregate(Sum("valorMovimiento"))
        egresos = (
            format(0, ".3f")
            if egresosUser["valorMovimiento__sum"] == None
            else egresosUser["valorMovimiento__sum"]
        )

        todays_date = date.today()
        ingresos_por_mes = obtener_ingresos_por_mes(request, todays_date.year)
        egresos_por_mes = obtener_egresos_por_mes(request, todays_date.year)
        ahorro_por_mes = obtener_ahorro_por_mes(request, todays_date.year)  
        total_ahorros =  sumar_ahorros(ahorro_por_mes)                                     

        # List of years of select
        years = list(range(datetime.date.today().year, 2015, -1))

        context = {
            "ingresos": ingresos,
            "egresos": egresos,
            "ingresos_por_mes": ingresos_por_mes,
            "egresos_por_mes": egresos_por_mes,
            "ahorro_por_mes": ahorro_por_mes,
            "total_ahorros": total_ahorros,
            "years": years,
        }

        return render(request, "index.html", context)

    else:
        theYear = request.POST.get("year")

        ingresosUser = Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=1, fechaMovimiento__contains=theYear
        ).aggregate(Sum("valorMovimiento"))
        ingresos = (
            format(0, ".3f")
            if ingresosUser["valorMovimiento__sum"] == None
            else ingresosUser["valorMovimiento__sum"]
        )

        egresosUser = Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=2, fechaMovimiento__contains=theYear
        ).aggregate(Sum("valorMovimiento"))
        egresos = (
            format(0, ".3f")
            if egresosUser["valorMovimiento__sum"] == None
            else egresosUser["valorMovimiento__sum"]
        )

        ingresos_por_mes = obtener_ingresos_por_mes(request, theYear)
        egresos_por_mes = obtener_egresos_por_mes(request, theYear)
        ahorro_por_mes = obtener_ahorro_por_mes(request, theYear) 
        total_ahorros =  sumar_ahorros(ahorro_por_mes)   

        years = list(range(datetime.date.today().year, 2015, -1))

        context = {
            "ingresos": ingresos,
            "egresos": egresos,
            "ingresos_por_mes": ingresos_por_mes,
            "egresos_por_mes": egresos_por_mes,
            "ahorro_por_mes": ahorro_por_mes,
            "total_ahorros": total_ahorros,
            "years": years,                        
            "theYear": theYear,
        }

        return render(request, "index.html", context)


def obtener_ingresos_por_mes(request, year):
    # Cálculo de ingresos por Mes
    ingresos_por_mes_query = (
        Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=1, fechaMovimiento__contains=year
        )
        .annotate(
            totalIngresos=Sum("valorMovimiento"),
            month=Extract("fechaMovimiento", "month"),
        )
        .values("totalIngresos", "month")
        .order_by("month")
    )
    ingresos_por_mes = [0 for x in range(1, 13)]

    for x in range(len(ingresos_por_mes_query)):
        objeto = ingresos_por_mes[ingresos_por_mes_query[x]["month"] - 1]
        if objeto != 0:
            ingresos_por_mes[ingresos_por_mes_query[x]["month"] - 1] = objeto + float(
                ingresos_por_mes_query[x]["totalIngresos"]
            )
        else:
            ingresos_por_mes[ingresos_por_mes_query[x]["month"] - 1] = float(
                ingresos_por_mes_query[x]["totalIngresos"]
            )

    return ingresos_por_mes


def obtener_egresos_por_mes(request, year):
    # Cálculo de Egresos por mes
    egresos_por_mes_query = (
        Movimiento.objects.filter(
            usuario=request.user, tipoMovimiento=2, fechaMovimiento__contains=year
        )
        .annotate(
            totalIngresos=Sum("valorMovimiento"),
            month=Extract("fechaMovimiento", "month"),
        )
        .values("totalIngresos", "month")
        .order_by("month")
    )
    egresos_por_mes = [0 for x in range(1, 13)]

    for x in range(len(egresos_por_mes_query)):
        objeto = egresos_por_mes[egresos_por_mes_query[x]["month"] - 1]
        if objeto != 0:
            egresos_por_mes[egresos_por_mes_query[x]["month"] - 1] = objeto + float(
                egresos_por_mes_query[x]["totalIngresos"]
            )
        else:
            egresos_por_mes[egresos_por_mes_query[x]["month"] - 1] = float(
                egresos_por_mes_query[x]["totalIngresos"]
            )

    return egresos_por_mes


def obtener_ahorro_por_mes(request, year):
    user= User.objects.values("id").filter(username=request.user)
    query = (        
        f"SELECT EXTRACT(month from fechaMovimiento) AS month_number,"
        f" sum( CASE WHEN tipoMovimiento_id = 1 THEN valorMovimiento WHEN tipoMovimiento_id = 2 THEN -valorMovimiento END ) as capital"
        f" FROM sistema_control_movimiento WHERE usuario_id = {user[0]['id']}"
        f" AND fechaMovimiento LIKE '%{year}%' GROUP BY month_number"
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        capital = cursor.fetchall()

    ahorro_por_mes = [0 for x in range(1, 13)]

    for x in range(len(capital)):        
        ahorro_por_mes[int(capital[x][0])-1] = float(capital[x][1])        
    
    return ahorro_por_mes


@login_required
def movimientos_usuario(request):

    if request.method != "POST":
        movimientos = Movimiento.objects.filter(usuario=request.user).order_by(
            "-fechaMovimiento"
        )
        movimientoForm = MovimientoForm()      
        categorias = Categorias.objects.filter(usuario=request.user)
        context = {"movimientos": movimientos, "form": movimientoForm, "categorias": categorias}
    else:
        form = MovimientoForm(data=request.POST)

        if form.is_valid():

            user = request.user
            tipoNuevoMovimientoId = request.POST["tipoMovimiento"]
            tipoNuevoMovimiento = TipoMovimiento.objects.get(id=tipoNuevoMovimientoId)
            categoria = request.POST["categoria"]            
            tipoCategoria = None if categoria == '0' else Categorias.objects.get(id=categoria)

            descripcionNuevoMovimiento = request.POST["descripcionMovimiento"]
            valorNuevoMovimiento = request.POST.get("valorMovimiento")

            fecha = request.POST["fechaMovimiento"]

            calculo = calculoNuevoCapital(
                request.user,
                int(valorNuevoMovimiento),
                tipoNuevoMovimiento.id,
                "nuevo",
                None,
            )
            if calculo:
                Movimiento.objects.create(
                    descripcionMovimiento=descripcionNuevoMovimiento,
                    fechaMovimiento=fecha,
                    tipoMovimiento=tipoNuevoMovimiento,
                    usuario=user,
                    valorMovimiento=valorNuevoMovimiento,
                    categoria = tipoCategoria
                )

                return HttpResponseRedirect(reverse("movimientos"))
            else:
                movimientos = Movimiento.objects.filter(usuario=request.user)
                movimientoForm = MovimientoForm()
                context = {
                    "movimientos": movimientos,
                    "form": movimientoForm,
                    "errores": True,
                }

    return render(request, "movimientos.html", context)


def calculoNuevoCapital(usuario, valorMovimiento, tipoMovimiento, accion, valorAnterior):
    estatus = False
    nuevoCapital = 0

    user = Profile.objects.get(user=usuario)
    capital = user.capitalTotal

    if accion == "nuevo":
        if tipoMovimiento == 1:
            nuevoCapital = capital + valorMovimiento
        elif tipoMovimiento == 2:
            nuevoCapital = capital - valorMovimiento

        user.capitalTotal = nuevoCapital
        user.save()

        estatus = True

    """elif accion == 'editar':        
        if tipoMovimiento == 2:
            if valorMovimiento > valorAnterior:
                nuevoCapital = capital - (valorMovimiento - valorAnterior)
            elif valorMovimiento < valorAnterior:
                nuevoCapital = capital + (valorAnterior -valorMovimiento)
            else:
                nuevoCapital = capital
        else:
            if capital < 0:
                if valorMovimiento > valorAnterior:
                    nuevoCapital = capital + (valorMovimiento - valorAnterior)
                elif valorMovimiento < valorAnterior:
                    nuevoCapital = capital - (valorAnterior - valorMovimiento)
                elif valorMovimiento == valorAnterior:
                    nuevoCapital = capital + (valorMovimiento + valorAnterior)
            else:
                pass

            if capital < 0:
                nuevoCapital = capital + (valorMovimiento + valorAnterior)                
            elif valorMovimiento > valorAnterior:
                nuevoCapital = capital + (valorMovimiento - valorAnterior)
            elif valorMovimiento < valorAnterior:
                nuevoCapital = capital - (valorAnterior -valorMovimiento)
            else:
                nuevoCapital = capital                   

        user.capitalTotal = nuevoCapital
        user.save()

        estatus = True"""

    return estatus


@login_required
def editar_movimiento(request, id):
    movimiento = Movimiento.objects.get(id=id)
    tipoMovimientoAnterior = movimiento.tipoMovimiento.id
    valorAnterior = movimiento.valorMovimiento
    categorias = Categorias.objects.filter(usuario=request.user)
    if request.method != "POST":
        form = EditarMovimientoForm(instance=movimiento)
        categoria = movimiento.categoria
        contexto = {"form": form, "categoria":categoria, "categorias": categorias}        
    else:
        form = EditarMovimientoForm(request.POST, instance=movimiento)        
        contexto = {"form": form}

        if form.is_valid():
            usuario = request.user
            tipoNuevoMovimientoId = request.POST["tipoMovimiento"]
            tipoMovimiento = TipoMovimiento.objects.get(id=tipoNuevoMovimientoId)
            descripcionMovimiento = request.POST.get("descripcionMovimiento")
            valorMovimiento = request.POST.get("valorMovimiento")

            categoria = request.POST["categoria"]            
            tipoCategoria = None if categoria == '0' else Categorias.objects.get(id=categoria)

            fecha = request.POST["fechaMovimiento"]

            if fecha > str(datetime.date.today()):  
                form = EditarMovimientoForm(instance=movimiento)
                contexto = {"form": form, "mensaje": "La fecha no puede ser posterior a la fecha de hoy" ,"errores": True}
            else:       
                user = Profile.objects.get(user=usuario)
                capital = user.capitalTotal                     

                try:
                    nuevoCapital = calcularCapitalMovimiento(float(valorAnterior), str(tipoMovimientoAnterior), float(valorMovimiento), tipoNuevoMovimientoId, float(capital))  
                    user.capitalTotal = nuevoCapital
                    user.save()                            
                    form.save()
                    movimiento.categoria = tipoCategoria
                    movimiento.save()

                    return HttpResponseRedirect(reverse("movimientos"))
                
                except:
                    form = EditarMovimientoForm(instance=movimiento)
                    contexto = {"form": form, "mensaje": "Ocurrió un error." ,"errores": True}
                
        else:
            form = EditarMovimientoForm(instance=movimiento)
            contexto = {"form": form, "errores": True}
    return render(request, "editarMovimiento.html", contexto)


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

    return redirect("movimientos")


@login_required
def ingresos_usuario(request):
    movimientos = (
        Movimiento.objects.all()
        .filter(usuario=request.user, tipoMovimiento=1)
        .order_by("-fechaMovimiento")
    )
    context = {"movimientos": movimientos}
    return render(request, "ingresos.html", context)


@login_required
def egresos_usuario(request):
    movimientos = (
        Movimiento.objects.all()
        .filter(usuario=request.user, tipoMovimiento=2)
        .order_by("-fechaMovimiento")
    )
    context = {"movimientos": movimientos}
    return render(request, "egresos.html", context)


def export_excel(request, nombre):
    return excel.export_excel(request, nombre)


def upload_excel(request):
    return excel.upload_excel(request)


def sumar_ahorros(array_ahorros):

    suma_total = 0
    for i in array_ahorros:
        if i > 0:
            suma_total = suma_total + i

    return str(suma_total)

@login_required
def perfil_usuario(request):
    if request.method == "POST":
        name = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        username = request.POST.get("username")
        correo = request.POST.get("correo")

        usuario = User.objects.get(id=request.user.id)
        usuario.first_name = name
        usuario.last_name = apellido
        usuario.username = username
        usuario.email = correo

        usuario.save()
        return HttpResponseRedirect(reverse("perfil"))

    else:
        context = {"error": ""}

    return render(request, "perfil.html", context)


@login_required
def cambiar_contrasena(request):
    usuario = User.objects.get(id=request.user.id)
    contrasenaActual = request.POST["contrasenaActual"]
    contrasenaNueva = request.POST["contrasenaNueva"]
    regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$|^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$|^(?=.*[a-z])(?=.*[A-Z])[a-zA-Z\d]{8,}$|^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    if check_password(contrasenaActual, usuario.password):
        if re.search(regex, contrasenaNueva):

            usuario.password = make_password(contrasenaNueva)
            usuario.save()

            return HttpResponseRedirect(reverse("logout"))
        else:
            context = {"error": "Ingrese una contraseña válida."}

    else:
        context = {"error": "La Contraseña Actual es incorrecta."}

    return render(request, "perfil.html", context)


def error_404_view(request, exception):       
    data = {"name": "ThePythonDjango.com"} 
    return render(request,'error_404.html')

@login_required
def programador_view(request):
    if request.method != "POST":
        movimientosProgramados = Programador.objects.filter(usuario=request.user).order_by(
            "fechaMovimientoProgramado"
        )
        programadorForm = ProgramadorForm()
        context = {"movimientos": movimientosProgramados, "form": programadorForm}
    else:
        form = ProgramadorForm(data=request.POST)

        if form.is_valid():

            user = request.user
            tipoNuevoMovimientoId = request.POST["tipoMovimiento"]
            tipoNuevoMovimiento = TipoMovimiento.objects.get(id=tipoNuevoMovimientoId)

            descripcionNuevoMovimiento = request.POST["descripcionMovimientoProgramado"]
            valorNuevoMovimiento = request.POST.get("valorMovimientoProgramado")

            fecha = request.POST["fechaMovimientoProgramado"]

            Programador.objects.create(
                    descripcionMovimientoProgramado=descripcionNuevoMovimiento,
                    fechaMovimientoProgramado=fecha,
                    tipoMovimiento=tipoNuevoMovimiento,
                    usuario=user,
                    valorMovimientoProgramado=valorNuevoMovimiento,
                )

            return HttpResponseRedirect(reverse("programador"))
        else:
                movimientos = Programador.objects.filter(usuario=request.user)
                movimientoForm = ProgramadorForm()
                context = {
                    "movimientos": movimientos,
                    "form": movimientoForm,
                    "errores": True,
                }

    return render(request, "programador.html", context)


@login_required
def eliminar_movimiento_programado(request, id):
    movimiento = Programador.objects.get(id=id)
    #usuario = Profile.objects.get(user=request.user)
    movimiento.delete()

    return redirect("programador")


@login_required
def editar_movimiento_programado(request, id):
    movimientoP = Programador.objects.get(id=id)
    valorAnterior = movimientoP.valorMovimientoProgramado
    if request.method != "POST":
        form = ProgramadorForm(instance=movimientoP)
        contexto = {"form": form, "fuente": "programador"}
    else:
        form = ProgramadorForm(request.POST, instance=movimientoP)
        contexto = {"form": form}

        if form.is_valid():            

            form.save()
            return HttpResponseRedirect(reverse("programador"))
        else:
                movimientos = Programador.objects.filter(usuario=request.user)
                movimientoForm = ProgramadorForm()
                context = {
                    "movimientos": movimientos,
                    "form": movimientoForm,
                    "errores": True,
                }            

    return render(request, "editarMovimiento.html", contexto)

@login_required
def categorias(request):
    user = request.user    
    
    if request.method != "POST":
        categorias = Categorias.objects.filter(usuario=request.user)
        form = CategoriasForm()
        diccionario = []
        diccionario.append({"name": "Ninguna", "cantidad": str(Movimiento.objects.filter(usuario=request.user, categoria=None).count())})        

        for categoria in categorias:            
            diccionario.append({"name": categoria.descripcion, "cantidad": str(Movimiento.objects.filter(categoria=categoria.id).count())})        

        contexto = {"categorias":categorias,"form": form, "diccionarioCats": diccionario}
    else:
        form = CategoriasForm(request.POST)
        contexto = {"form": form}

        if form.is_valid():            
            descripcion = request.POST["descripcion"]

            Categorias.objects.create(
                    descripcion = descripcion,
                    usuario=user,
                )
                     
            return HttpResponseRedirect(reverse("categorias"))
        else:
                categorias = Categorias.objects.filter(usuario=request.user)
                form = CategoriasForm()
                context = {
                    "categorias": categorias,
                    "form": form,
                    "errores": True,
                }                

    return render(request, "categorias.html", contexto)

@login_required
def editarCategoria(request, id):
    categoria = Categorias.objects.get(id=id)    
    if request.method != "POST":
        form = CategoriasForm(instance=categoria)
        contexto = {"form": form}
    else:
        form = CategoriasForm(request.POST, instance=categoria)
        contexto = {"form": form}

        if form.is_valid():            

            form.save()
            return HttpResponseRedirect(reverse("categorias"))
        else:
                categoria = Categorias.objects.filter(usuario=request.user)
                categoriaForm = CategoriasForm()
                context = {
                    "movimientos": categoria,
                    "form": categoriaForm,
                    "errores": True,
                }            

    return render(request, "editarCategoria.html", contexto)

@login_required
def eliminarCategoria(request, id):
    categoria = Categorias.objects.get(id=id)    
    categoria.delete()

    return redirect("categorias")
    