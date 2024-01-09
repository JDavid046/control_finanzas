import csv
import datetime
from django.shortcuts import render
from django.urls import reverse
import xlwt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from sistema_control.forms import MovimientoForm
from sistema_control.models import Movimiento, Profile, TipoMovimiento, Categorias

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
        categoria = Categorias.objects.get(descripcion=prmCategoria)
        categoriaRetorno = categoria
    except:
        Categorias.objects.create(
                    descripcion = prmCategoria,
                    usuario=prmUser,
                )
        categoriaRetorno = Categorias.objects.get(descripcion=prmCategoria)
    
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
            writer.writerow([str(row[0]), rowDescripcion, str(row[2]), str(row[3]), str(row[4])])        

        return response


    def upload_excel(request):
        usuario = User.objects.get(id=request.user.id)    
        data = {}
        if "POST" == request.method:
            
            try:
                csv_file = request.FILES["csv_file"]
                if not csv_file.name.endswith('.csv'):
                    movimientoForm = MovimientoForm()
                    movimientos = Movimiento.objects.filter(usuario=request.user)
                    context = {
                            "movimientos": movimientos,
                            "mensaje": "El archivo debe ser un archivo .csv",
                            "errores": True,
                            "form": movimientoForm
                        }
                    
                #if file is too large, return
                elif csv_file.multiple_chunks():
                    movimientoForm = MovimientoForm()
                    movimientos = Movimiento.objects.filter(usuario=request.user)
                    context = {
                            "movimientos": movimientos,
                            "mensaje": "El archivo supera el peso permitido.",
                            "errores": True,
                            "form": movimientoForm
                        }
                else:
                    
                    file_data = csv_file.read().decode("utf-8")
                    
                    lines = file_data.split("\n")[1:]
                    
                    for line in lines:
                        if(str(line).strip() != ''):
                            fields = line.split("|")
                            data_dict = {}
                            data_dict["tipoMovimiento"] = fields[0]
                            data_dict["descripcionMovimiento"] = fields[1]
                            data_dict["valorMovimiento"] = fields[2]
                            data_dict["fechaMovimiento"] = str(fields[3]).strip()
                            data_dict["usuario"] = usuario
                            laCategoria = str(fields[4]).strip()

                            try:
                                form = MovimientoForm(data_dict)                
                                if form.is_valid():
                                    calculo = calculoNuevoCapital(
                                        request.user,
                                        int(data_dict["valorMovimiento"].split('.')[0]),
                                        int(data_dict["tipoMovimiento"]),
                                        "nuevo",
                                        None,
                                    )
                                if calculo:

                                    Movimiento.objects.create(
                                        descripcionMovimiento=data_dict["descripcionMovimiento"],
                                        fechaMovimiento=data_dict["fechaMovimiento"],
                                        tipoMovimiento = TipoMovimiento.objects.get(id=data_dict["tipoMovimiento"]),
                                        usuario=data_dict["usuario"],
                                        valorMovimiento=data_dict["valorMovimiento"],
                                        categoria = verificarCategoria(laCategoria, request.user)
                                    )

                            except Exception as e:                
                                pass                 

                    return HttpResponseRedirect(reverse("movimientos"))                    
                    
            except Exception as e:
                pass
                
        return render(request, "movimientos.html", context)
    
    