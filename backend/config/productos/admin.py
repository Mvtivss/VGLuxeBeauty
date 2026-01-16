from django.contrib import admin
from .models import Producto

# Register your models here.

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'activo', 'creado')
    list_filter = ('categoria', 'activo', 'creado')
    search_fields = ('nombre', 'categoria')
