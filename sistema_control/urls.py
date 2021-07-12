from django.contrib.auth import login, logout
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/', views.olvide_contrasena, name='password'),
    path('movimientos/', views.movimientos_usuario, name='movimientos'),
    path('ingresos/', views.ingresos_usuario, name='ingresos'),
    path('egresos/', views.egresos_usuario, name='egresos'),
    path('export-excel/<str:nombre>/', views.export_excel, name='export-excel'),
    path('perfil/', views.perfil_usuario, name='perfil'),    
]