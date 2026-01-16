from django.db import models

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
