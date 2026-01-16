from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Producto
from .serializers import ProductoSerializer
from django.shortcuts import get_object_or_404

# Create your views here.
def home (request):
    productos = Producto.objects.filter(activo=True)[:6]  # Mostrar máximo 6 productos
    return render (request, "index.html", {'productos': productos})

class ProductoListView(ListAPIView):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer

def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)
    return render(request, "producto_detalle.html", {'producto': producto})