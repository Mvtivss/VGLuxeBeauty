from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=80)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to="productos/")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class Resena(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) #1 a 5 estrellas
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False) #Requiere aprobacion del admin

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
    
    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre} - ({self.calificacion} ★ )'
    
    def estrellas_html(self):
        estrellas_llenas = '★' * self.calificacion
        estrellas_vacias = '☆' * (5 - self.calificacion)
        return estrellas_llenas + estrellas_vacias

class Testimonio(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="testimonios/", null=True, blank=True)
    comentario = models.TextField()
    red_social = models.CharField(max_length=50, choices=[
        ('Instagram', 'Instagram'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('TikTok', 'TikTok'),
        ('otro', 'Otro'),
    ], default='Instagram')
    calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5) #1 a 5 estrellas
    fecha = models.DateTimeField(auto_now_add=True)
    destacado = models.BooleanField(default=False) #Para mostrar en la pagina principal
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Testimonio'
        verbose_name_plural = 'Testimonios'

    def __str__(self):
        return f'{self.nombre} - ({self.red_social}) ({self.calificacion} ★ )'
    
    def estrellas_html(self):
        estrellas_llenas = '★' * self.calificacion
        estrellas_vacias = '☆' * (5 - self.calificacion)
        return estrellas_llenas + estrellas_vacias

class Carrito(models.Model):
        usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
        session_key = models.CharField(max_length=40, null=True, blank=True)
        creado = models.DateTimeField(auto_now_add=True)
        actualizado = models.DateTimeField(auto_now=True)

        class Meta:
            verbose_name = 'Carrito'
            verbose_name_plural = 'Carritos'

        def __str__(self):
            if self.usuario:
                return f'Carrito de {self.usuario.username}'
            return f'Carrito {self.id}'
        
        @property
        def total_items(self):
            return sum(item.cantidad for item in self.items.all())
        
        @property
        def total_precio(self):
            return sum(item.subtotal for item in self.items.all())
        
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ('carrito', 'producto')

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad