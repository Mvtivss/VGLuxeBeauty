from django.urls import path
from .views import ProductoListView
from .views import producto_detalle


urlpatterns = [
    path ("productos/", ProductoListView.as_view(), name="productos"),
    path ("producto/<int:id>/", producto_detalle, name="producto_detalle"),
]