import csv
import datetime
from django.shortcuts import render
from django.urls import reverse
import xlwt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from sistema_control.forms import MovimientoForm
from sistema_control.models import Movimiento, Profile, TipoMovimiento, Categorias
from io import StringIO
from django.db import transaction

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
        return estatus

def verificarCategoria(prmCategoria, prmUser):    
    categoriaRetorno = None

    if(prmCategoria == "None"): return categoriaRetorno

    try:
        categoria = Categorias.objects.get(descripcion=prmCategoria, usuario=prmUser)
        categoriaRetorno = categoria
    except:
        Categorias.objects.create(
                    descripcion = prmCategoria,
                    usuario=prmUser,
                )
        categoriaRetorno = Categorias.objects.get(descripcion=prmCategoria, usuario=prmUser)
    
    return categoriaRetorno

class excel:  
              
    def export_excel(request, nombre):
        response = HttpResponse(content_type="text/csv")

        response["Content-Disposition"] = (
            'attachment; filename="'
            + nombre
            + ' de "'
            + request.user.username
            + " "
            + str(datetime.datetime.now())
            + ".csv"
        )

        writer = csv.writer(response, delimiter="|")


        wb = xlwt.Workbook(encoding="UTF-8-SIG")
        ws = wb.add_sheet(nombre)        
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = [
            "Tipo de Movimiento",
            "Descripción del Movimiento",
            "Valor del Movimiento",
            "Fecha del movimiento",
            "Categoría",
        ]

        writer.writerow(['Tipo de Movimiento','Descripcion del Movimiento','Valor del Movimiento','Fecha del Movimiento', 'Categoría'])   

        font_style = xlwt.XFStyle()

        switch_tabla = {
            "movimiento": Movimiento.objects.all()
            .filter(usuario=request.user)
            .values_list(
                "tipoMovimiento",
                "descripcionMovimiento",
                "valorMovimiento",
                "fechaMovimiento",
                "categoria__descripcion",
            ),
            "ingreso": Movimiento.objects.all()
            .filter(usuario=request.user, tipoMovimiento=1)
            .values_list(
                "tipoMovimiento__nombreTipoMovimiento",
                "descripcionMovimiento",
                "valorMovimiento",
                "fechaMovimiento",
                "categoria__descripcion",
            ),
            "egreso": Movimiento.objects.all()
            .filter(usuario=request.user, tipoMovimiento=2)
            .values_list(
                "tipoMovimiento__nombreTipoMovimiento",
                "descripcionMovimiento",
                "valorMovimiento",
                "fechaMovimiento",
                "categoria__descripcion",
            ),
        }

        rows = None

        if nombre == "Movimientos":
            rows = switch_tabla["movimiento"]
        elif nombre == "Ingresos":
            rows = switch_tabla["ingreso"]
        elif nombre == "Egresos":
            rows = switch_tabla["egreso"]

        for row in rows:
            rowDescripcion = str(row[1]).replace('\n', ' ').replace('\r','')
            rowValor = str(row[2]).split('.')[0]
            writer.writerow([str(row[0]), rowDescripcion, rowValor, str(row[3]), str(row[4])])        

        return response


    def upload_excel(request):
        usuario = request.user

        if request.method == "POST":

            try:
                file = request.FILES["csv_file"]

                if not file.name.endswith(".csv"):
                    return render(request, "movimientos.html", {
                        "mensaje": "El archivo debe ser .csv",
                        "errores": True,
                        "form": MovimientoForm()
                    })

                if file.multiple_chunks():
                    return render(request, "movimientos.html", {
                        "mensaje": "El archivo es demasiado grande",
                        "errores": True,
                        "form": MovimientoForm()
                    })

                decoded = file.read().decode("utf-8")
                io_string = StringIO(decoded)
                reader = csv.reader(io_string, delimiter="|")

                next(reader)  # saltar header

                movimientos = []

                for row in reader:
                    if not row:
                        continue

                    tipo = int(row[0])
                    descripcion = row[1]
                    valor = float(row[2])
                    fecha = row[3].strip()
                    categoria_raw = row[4].strip()

                    # lógica externa (idealmente debería optimizarse también)
                    calculo = calculoNuevoCapital(
                        usuario,
                        int(str(valor).split('.')[0]),
                        tipo,
                        "nuevo",
                        None,
                    )

                    if calculo:
                        movimientos.append(
                            Movimiento(
                                descripcionMovimiento=descripcion,
                                fechaMovimiento=fecha,
                                tipoMovimiento_id=tipo,
                                usuario=usuario,
                                valorMovimiento=valor,
                                categoria=verificarCategoria(categoria_raw, usuario)
                            )
                        )
                
                with transaction.atomic():
                    Movimiento.objects.bulk_create(movimientos, batch_size=1000)

                return HttpResponseRedirect(reverse("movimientos"))

            except Exception as e:                
                print("ERROR UPLOAD:", str(e))
                return render(request, "movimientos.html", {
                    "mensaje": "Error procesando archivo",
                    "errores": True,
                    "form": MovimientoForm()
                })

        return render(request, "movimientos.html", {
            "form": MovimientoForm()
        })
    
    