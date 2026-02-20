from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Pedido, DireccionEnvio,  ItemPedido
from .forms import DireccionEnvioForm, CheckoutForm
from productos.models import Carrito
from productos.views import obtener_carrito

# Create your views here.
@login_required
def checkout(request):
    """Vista del proceso de checkout."""
    carrito = obtener_carrito(request)

    # Verificar que el carrito no este vacio
    if not carrito.items.exists():
        messages.warning(request, 'Tu carrito esta vacio.')
        return redirect('ver_carrito')
    
    # Verificar stock disponible
    for item in carrito.items.all():
        if item.cantidad > item.producto.stock:
            messages.error(request, f'No hay suficiente stock de {item.producto.nombre}')
            return redirect('ver_carrito')
        
    # Obtener direccionees guardadas del usuario
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST, usuario=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Obtener datos de dirección
                    if form.cleaned_data['usar_direccion_guardada']:
                        direccion_id = form.cleaned_data['direccion_id']
                        direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
                        direccion_data = {
                            'nombre_completo': direccion.nombre_completo,
                            'telefono': direccion.telefono,
                            'direccion': direccion.direccion,
                            'referencia': direccion.referencia,
                            'comuna': direccion.comuna,
                            'region': direccion.region,
                            'codigo_postal': direccion.codigo_postal,
                            'pais': direccion.pais,
                        }
                    else:
                        direccion_data = {
                            'nombre_completo': form.cleaned_data['nombre_completo'],
                            'telefono': form.cleaned_data['telefono'],
                            'direccion': form.cleaned_data['direccion'],
                            'referencia': form.cleaned_data.get('referencia', ''),
                            'comuna': form.cleaned_data['comuna'],
                            'region': form.cleaned_data['region'],
                            'codigo_postal': form.cleaned_data.get('codigo_postal', ''),
                            'pais': 'Chile',
                        }
                        # Guardar dirección si se solicitó
                        if form.cleaned_data['guardar_direccion']:
                            DireccionEnvio.objects.create(
                                usuario=request.user,
                                **direccion_data
                            )
                    
                    # Calcular totales (Chile - envío gratis sobre $50.000 CLP)
                    subtotal = int(carrito.total_precio)
                    costo_envio = 5000 if subtotal < 50000 else 0
                    total = subtotal + costo_envio

                    # Crear el pedido
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        subtotal=subtotal,
                        costo_envio=costo_envio,
                        total=total,
                        metodo_pago=form.cleaned_data['metodo_pago'],
                        notas=form.cleaned_data['notas'],
                        **direccion_data
                    )

                    # Crear items del pedido y actualizar stock
                    for item in carrito.items.all():
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=item.producto,
                            nombre_producto=item.producto.nombre,
                            precio_unitario=int(item.producto.precio),
                            cantidad=item.cantidad
                        )

                        # Reducir stock
                        item.producto.stock -= item.cantidad
                        item.producto.save()

                    # Vaciar el carrito
                    carrito.items.all().delete()

                    messages.success(request, f'¡Pedido #{pedido.numero_pedido} creado exitosamente!')
                    return redirect('pedido_confirmacion', pedido_id=pedido.id)
                    
            except Exception as e:
                messages.error(request, f'Error al procesar el pedido: {str(e)}')
                return redirect('checkout')
    else:
        form = CheckoutForm(usuario=request.user)
    
    # Calcular costos para preview
    subtotal = int(carrito.total_precio)
    costo_envio = 5000 if subtotal < 50000 else 0
    total = subtotal + costo_envio

    context = {
        'form': form,
        'carrito': carrito,
        'items': carrito.items.all(),
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
        'direcciones': direcciones,
        'envio_gratis_desde': 50000,
    }

    return render(request, 'pedidos/checkout.html', context)


@login_required
def pedido_confirmacion(request, pedido_id):
    """Vista de confirmación del pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    context = {
        'pedido': pedido,
    }

    return render(request, 'pedidos/confirmacion.html', context)


@login_required
def mis_pedidos(request):
    """Lista de pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('items')

    context = {
        'pedidos': pedidos,
    }

    return render(request, 'pedidos/mis_pedidos.html', context)


@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    context = {
        'pedido': pedido,
    }

    return render(request, 'pedidos/detalle_pedido.html', context)
@login_required
def cancelar_pedido(request, pedido_id):
    """Cancelar un pedido (solo si está pendiente)"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    if pedido.estado in ['pendiente', 'pagado']:
        with transaction.atomic():
            # Devolver stock
            for item in pedido.items.all():
                item.producto.stock += item.cantidad
                item.producto.save()
            
            pedido.estado = 'cancelado'
            pedido.save()
            
            messages.success(request, f'Pedido #{pedido.numero_pedido} cancelado exitosamente')
    else:
        messages.error(request, 'No se puede cancelar este pedido')
    
    return redirect('detalle_pedido', pedido_id=pedido.id)


# Vistas para gestión de direcciones
@login_required
def mis_direcciones(request):
    """Lista de direcciones del usuario"""
    direcciones = DireccionEnvio.objects.filter(usuario=request.user)
    
    context = {
        'direcciones': direcciones,
    }
    
    return render(request, 'pedidos/mis_direcciones.html', context)


@login_required
def agregar_direccion(request):
    """Agregar nueva dirección"""
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = request.user
            direccion.save()
            messages.success(request, 'Dirección agregada exitosamente')
            return redirect('mis_direcciones')
    else:
        form = DireccionEnvioForm()
    
    context = {
        'form': form,
        'accion': 'Agregar'
    }
    
    return render(request, 'pedidos/form_direccion.html', context)


@login_required
def editar_direccion(request, direccion_id):
    """Editar dirección existente"""
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada exitosamente')
            return redirect('mis_direcciones')
    else:
        form = DireccionEnvioForm(instance=direccion)
    
    context = {
        'form': form,
        'accion': 'Editar',
        'direccion': direccion
    }
    
    return render(request, 'pedidos/form_direccion.html', context)


@login_required
def eliminar_direccion(request, direccion_id):
    """Eliminar dirección"""
    direccion = get_object_or_404(DireccionEnvio, id=direccion_id, usuario=request.user)
    direccion.delete()
    messages.success(request, 'Dirección eliminada exitosamente')
    return redirect('mis_direcciones')