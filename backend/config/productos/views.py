from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Producto
from .serializers import ProductoSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from .models import Testimonio
from django.core.paginator import Paginator

# Create your views here.
def home (request):
    productos = Producto.objects.filter(activo=True)[:8]  # Mostrar máximo 8 productos
    testimonios = Testimonio.objects.filter(activo=True, destacado=True)[:6]  # Mostrar máximo 6 testimonios
    
    context = {
        'productos': productos,
        'testimonios': testimonios
    }
    
    return render (request, "index.html", context)

class ProductoListView(ListAPIView):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer

def producto_detalle(request, id):
    producto = get_object_or_404(Producto, id=id)

    #Obtener reseñas aprobadas
    resenas = producto.resenas.filter(aprobada=True)

    #Calcular promedio y total de reseñas
    stats = resenas.aggregate(
        promedio=Avg('calificacion'),
        total=Count('id')
    )

    context = {
        'producto': producto,
        'resenas': resenas,
        'promedio_calificacion': round(stats['promedio'], 1) if stats['promedio'] else 0,
        'total_resenas': stats['total']
    }
    

    return render(request, "producto_detalle.html", context)

def productos(request):
    #Obtener todos los productos activos
    productos_list = Producto.objects.filter(activo=True)

    #Filtros
    categoria = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    orden = request.GET.get('orden', 'reciente')

    #Aplicar filtro de categoria
    if categoria:
        productos_list = productos_list.filter(categoria=categoria)
    
    #Aplicar busqueda
    if busqueda:
        productos_list = productos_list.filter(
            nombre__icontains=busqueda
        ) | productos_list.filter(
            descripcion__icontains=busqueda
        )
    #Aplicar ordenamiento 
    if orden == 'precio_menor':
        productos_list = productos_list.order_by('precio')
    elif orden == 'precio_mayor':
        productos_list = productos_list.order_by('-precio')
    elif orden == 'nombre':
        productos_list = productos_list.order_by('nombre')
    else:  #orden reciente por defecto
        productos_list = productos_list.order_by('-creado')
    
    #Paginacion
    paginator = Paginator(productos_list, 12) #12 productos por pagina
    page_number = request.GET.get('page')
    productos_paginados = paginator.get_page(page_number)

    #Obtener categorias unicas
    categorias = Producto.objects.filter(activo=True).values_list('categoria', flat=True).distinct()

    context = {
        'productos': productos_paginados,
        'categorias': categorias,
        'categoria_actual': categoria,
        'busqueda': busqueda,
        'orden': orden
    }

    return render (request, "productos.html", context)