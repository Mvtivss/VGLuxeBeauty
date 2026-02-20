
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from .models import Producto
from .serializers import ProductoSerializer
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg, Count
from .models import Testimonio, Producto, Resena, Carrito, ItemCarrito
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST


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

def obtener_carrito(request):
    """Obtiene o crea el carrito del usuario/sesion."""
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        carrito, created = Carrito.objects.get_or_create(session_key=session_key)
    return carrito

@require_POST
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito."""
    producto = get_object_or_404(Producto, id=producto_id)

    if producto.stock <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Producto agotado.'
            })
        messages.error(request, 'Producto agotado.')
        return redirect('productos')
    
    carrito = obtener_carrito(request)

    # Obtener o crear item
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 1}
    )

    if not created:
        if item.cantidad < producto.stock:
            item.cantidad += 1
            item.save()
            mensaje = f'{producto.nombre} agregado al carrito (cantidad {item.cantidad}).'
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'No hay mas stock disponible.'
                })
            messages.warning(request, 'No hay mas stock disponible.')
            return redirect('productos')
        
    else:
        mensaje = f'{producto.nombre} agregado al carrito.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'total_items': carrito.total_items,
        })
    
    messages.success(request, mensaje)
    return redirect('productos')

def ver_carrito(request):
    """Ver el contenido del carrito."""
    carrito = obtener_carrito(request)

    context = {
        'carrito': carrito,
        'items': carrito.items.select_related('producto').all(),
        'total': carrito.total_precio,
    }
    return render(request, 'carrito.html', context)

@require_POST
def actualizar_cantidad(request, item_id):
    """"Actualizar cantidad e un item en el carrito"""
    item = get_object_or_404(ItemCarrito, id=item_id)
    carrito = obtener_carrito(request)

    # Verificar que el item pertenezca al carrito del usuario/sesion
    if item.carrito != carrito:
        return JsonResponse({'success': False, 'message': 'Item no pertenece al carrito.'})
    
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        item.delete()
        mensaje = f'{item.producto.nombre} eliminado del carrito.'
    elif cantidad > item.producto.stock:
        return JsonResponse({
            'success': False,
            'message': f'Solo hay {item.producto.stock} unidades disponibles en stock.'
        })
    else:
        item.cantidad = cantidad
        item.save()
        mensaje = f'Cantidad de {item.producto.nombre} actualizada a {item.cantidad}.'

    return JsonResponse({
        'success': True,
        'message': mensaje,
        'subtotal': item.subtotal if cantidad > 0 else 0,
        'total': carrito.total_precio,
        'total_items': carrito.total_items,   
         })

@require_POST
def eliminar_del_carrito(request, item_id):
    """Eliminar un item del carrito."""
    item = get_object_or_404(ItemCarrito, id=item_id)
    carrito = obtener_carrito(request)

    if item.carrito != carrito:
        return JsonResponse({'success': False, 'message': 'Item no pertenece al carrito.'}) 

    producto_nombre = item.producto.nombre
    item.delete()

    if request.headers.get('x-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{producto_nombre} eliminado del carrito.',
            'total': carrito.total_precio,
            'total_items': carrito.total_items,
        })

    messages.success(request, f'{producto_nombre} eliminado del carrito.')
    return redirect('ver_carrito')

def contador_carrito(request):
    """Obtener numero de items en el carrito (para AJAX)"""
    carrito = obtener_carrito(request)
    return JsonResponse({'total_items': carrito.total_items})

def vaciar_carrito(request):
    """Vaciar todo el carrito"""
    carrito = obtener_carrito(request)
    carrito.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('ver_carrito')

def nosotros(request):
    """Vista para la página Nosotros"""
    return render(request, 'nosotros.html')

def contacto(request):
    """Vista para la página de Contacto"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        # Aquí puedes agregar lógica para enviar email o guardar en BD
        # Por ahora solo mostramos un mensaje de éxito
        messages.success(request, f'Gracias {nombre}, tu mensaje ha sido enviado. Te responderemos pronto.')
        return redirect('contacto')
    
    return render(request, 'contacto.html')