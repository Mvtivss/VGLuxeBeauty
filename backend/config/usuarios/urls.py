from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
     path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos_usuario'),
    
    # Recuperación de contraseña
    path('recuperar-password/', views.RecuperarPasswordView.as_view(), name='password_reset'),
    path('recuperar-password/enviado/', 
         lambda request: render(request, 'usuarios/recuperar_password_done.html'),
         name='password_reset_done'),
    path('recuperar-password/confirmar/<uidb64>/<token>/', 
         views.RecuperarPasswordConfirmView.as_view(),
         name='password_reset_confirm'),
    path('recuperar-password/completado/',
         lambda request: render(request, 'usuarios/recuperar_password_complete.html'),
         name='password_reset_complete'),
]
