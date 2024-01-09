from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Categorias(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=40)
    usuario = models.ForeignKey(User, null=True, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.descripcion

class TipoMovimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombreTipoMovimiento = models.CharField(max_length=7)

    def __str__(self):
        return self.nombreTipoMovimiento

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capitalTotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)    

    def __str__(self):
        return self.user.username

class Movimiento(models.Model):
    id = models.AutoField(primary_key=True)    
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    tipoMovimiento = models.ForeignKey(TipoMovimiento, null=False, blank=False, on_delete=models.RESTRICT)
    descripcionMovimiento = models.TextField()
    valorMovimiento = models.DecimalField(max_digits=20, decimal_places=2)
    fechaMovimiento = models.DateField()
    categoria = models.ForeignKey(Categorias, null=True, blank=False, on_delete=models.SET_NULL)

    def __str__(self):
        return self.tipoMovimiento.nombreTipoMovimiento + " - "+  self.usuario.username       

class Programador(models.Model):
    id = models.AutoField(primary_key=True)    
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    tipoMovimiento = models.ForeignKey(TipoMovimiento, null=False, blank=False, on_delete=models.RESTRICT)
    descripcionMovimientoProgramado = models.TextField()
    valorMovimientoProgramado = models.DecimalField(max_digits=20, decimal_places=2)
    fechaMovimientoProgramado = models.IntegerField()
    ultimaFechaEjecucion = models.DateField(null=True)
