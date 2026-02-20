from django.urls import path
from . import views


urlpatterns = [
    path ('', views.home , name="home"),
    path ("productos/", views.productos , name="productos"),
    path ("producto/<int:id>/", views.producto_detalle, name="producto_detalle"),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/contador/', views.contador_carrito, name='contador_carrito'),
]
