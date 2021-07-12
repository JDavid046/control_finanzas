from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import fields
from django.forms import widgets
from django.forms.fields import EmailField
import datetime
from .models import *

class UserRegisterForm(UserCreationForm):    

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmación de Contraseña'})         

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']        

        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Ej: Usuario01'}),
            'email': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Ej: correo@gmail.com'}),                     
        }

        help_texts = {k:"" for k in fields }                       

    

class UserLoginForm(forms.ModelForm):  
    class Meta:
        model = User
        fields = ['username', 'password']

        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'password': forms.PasswordInput(attrs={'class':'form-control'})
        }

        help_texts = {k:"" for k in fields }


class MovimientoForm(forms.ModelForm):

    AVAILABLE_YEAR_CHOICES = list(range(2010, datetime.date.today().year+1))
    fechaMovimiento = forms.DateField(initial=datetime.date.today(), widget=forms.SelectDateWidget(years=AVAILABLE_YEAR_CHOICES))

    class Meta:
        model = Movimiento
        fields = ['tipoMovimiento', 'descripcionMovimiento', 'valorMovimiento']

        widgets = {
            'tipoMovimiento': forms.Select(attrs={'class':'form-select'}),
            'descripcionMovimiento': forms.Textarea(attrs={'class':'form-control'}),
            'valorMovimiento': forms.NumberInput(attrs={'class':'form-control', 'min':'0'}),            
        }