from django.contrib.auth import login, logout
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('credentials/<str:accion>', views.olvide_credenciales, name='credentials'),    
    path('movimientos/', views.movimientos_usuario, name='movimientos'),
    path('editar-movimiento/<int:id>/', views.editar_movimiento, name='editarMovimiento'),
    path('eliminar-movimiento/<int:id>/', views.eliminar_movimiento, name='eliminarMovimiento'),
    path('ingresos/', views.ingresos_usuario, name='ingresos'),
    path('egresos/', views.egresos_usuario, name='egresos'),
    path('programador/', views.programador_view, name='programador'),
    path('eliminar-movimientoProgramado/<int:id>/', views.eliminar_movimiento_programado, name='eliminarMovimientoProgramado'),
    path('export-excel/<str:nombre>/', views.export_excel, name='export-excel'),
    path('upload-excel', views.upload_excel, name='upload-excel'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiarContrasena'),    
    path('editar-movimiento-programado/<int:id>/', views.editar_movimiento_programado, name='editarMovimientoProgramado'),
    path('categorias/', views.categorias, name='categorias'),    
    path('editarCategoria/<int:id>/', views.editarCategoria, name='editarCategoria'),
    path('eliminarCategoria/<int:id>/', views.eliminarCategoria, name='eliminarCategoria')    
]