from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TipoMovimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombreTipoMovimiento = models.CharField(max_length=7)

    def __str__(self):
        return self.nombreTipoMovimiento

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    capitalTotal = models.DecimalField(max_digits=20, decimal_places=3, default=0)
    deudas = models.DecimalField(max_digits=20, decimal_places=3, default=0)

    def __str__(self):
        return self.user.username

"""class Usuario(models.Model):
    documento = models.IntegerField(primary_key=True)
    nombreUsuario = models.CharField(max_length=60)
    apellidoUsuario = models.CharField(max_length=120)
    fechaNacimiento = models.DateField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    tipoUsuario = models.ForeignKey(TipoUsuario, null=False, blank=False, on_delete=models.CASCADE)        
    capitalTotal = models.DecimalField(max_digits=20, decimal_places=3)

    def __str__(self):
        return self.email"""

class Movimiento(models.Model):
    id = models.AutoField(primary_key=True)    
    usuario = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    tipoMovimiento = models.ForeignKey(TipoMovimiento, null=False, blank=False, on_delete=models.CASCADE)
    descripcionMovimiento = models.TextField()
    valorMovimiento = models.DecimalField(max_digits=20, decimal_places=3)
    fechaMovimiento = models.DateField()

    def __str__(self):
        return self.tipoMovimiento.nombreTipoMovimiento + " - "+  self.usuario.username       