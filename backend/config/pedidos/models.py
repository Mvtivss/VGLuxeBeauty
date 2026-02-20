from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto
from django.utils import timezone



# Create your models here.

class DireccionEnvio(models.Model):
    """Direcciones de envío guardadas por el usuario"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direcciones')
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)  
    direccion = models.CharField(max_length=300, help_text="Calle y número")
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Chile')
    referencia = models.CharField(max_length=300, blank=True, null=True, help_text="Depto, block, etc.")
    predeterminada = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dirección de Envío"
        verbose_name_plural = "Direcciones de Envío"
        ordering = ['-predeterminada', '-creada']

    def __str__(self):
        return f'{self.nombre_completo} - {self.comuna}, {self.region}'
    
    def save(self, *args, **kwargs):
        # Si se marca como predeterminada, desmarcar las demás
        if self.predeterminada:
            DireccionEnvio.objects.filter(usuario=self.usuario, predeterminada=True).update(predeterminada=False)
        super().save(*args, **kwargs)

class Pedido(models.Model):
    """Pedido realizado por un usuario."""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    METODO_PAGO_CHOICES = [
        ('webpay', 'Webpay Plus (Tarjeta)'),
        ('transferencia', 'Transferencia Bancaria'),
        ('mercadopago', 'Mercado Pago'),
        ('khipu', 'Khipu'),
        ('efectivo', 'Pago contra entrega'),
    ]

    # Información del pedido
    numero_pedido = models.CharField(max_length=20, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')

    # Dirección de envío (formato chileno)
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=300)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Chile')
    referencia = models.CharField(max_length=300, blank=True, null=True)

    #Estado y pago
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, null=True, blank=True)

    # Montos (CLP - Pesos Chilenos)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0)

    # Notas y referencias 
    notas = models.TextField(blank=True, null=True)
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)

    # Fechas
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-creado']

    def __str__(self):
        return f'Pedido #{self.numero_pedido} - {self.usuario.username}'
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            import random
            import string
            timestamp = timezone.now().strftime('%Y%m%d')
            random_suffix = ''.join(random.choices(string.digits, k=4))
            self.numero_pedido = f'VGL{timestamp}{random_suffix}'
        super().save(*args, **kwargs)

    @property
    def direccion_completa(self):
        partes = [self.direccion]
        if self.referencia:
            partes.append(self.referencia)
        partes.extend([self.comuna, self.region])
        if self.codigo_postal:
            partes.append(self.codigo_postal)
        partes.append(self.pais)
        return ', '.join(partes)
    
    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())
        
class ItemPedido(models.Model):
    """Item individual dentro de un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    # Guardar información del producto en el momento de la compra 
    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)  # CLP sin decimales
    cantidad = models.PositiveIntegerField(default=1)

    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return f'{self.cantidad}x {self.nombre_producto} - Pedido #{self.pedido.numero_pedido}'
    
    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def save(self, *args, **kwargs):
        if not self.nombre_producto:
            self.nombre_producto = self.producto.nombre
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)
