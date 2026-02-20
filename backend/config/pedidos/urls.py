from django.urls import path
from . import views

urlpatterns = [
    # Checkout y confirmación
    path('checkout/', views.checkout, name='checkout'),
    path('confirmacion/<int:pedido_id>/', views.pedido_confirmacion, name='pedido_confirmacion'),
    
    # Gestión de pedidos
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
    
    # Gestión de direcciones
    path('direcciones/', views.mis_direcciones, name='mis_direcciones'),
    path('direcciones/agregar/', views.agregar_direccion, name='agregar_direccion'),
    path('direcciones/<int:direccion_id>/editar/', views.editar_direccion, name='editar_direccion'),
    path('direcciones/<int:direccion_id>/eliminar/', views.eliminar_direccion, name='eliminar_direccion'),
]