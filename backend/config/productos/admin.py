from django.contrib import admin
from .models import Producto, Testimonio, Resena, Carrito, ItemCarrito

# Register your models here.

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'activo', 'creado')
    list_filter = ('categoria', 'activo', 'creado')
    search_fields = ('nombre', 'categoria')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'calificacion', 'fecha', 'aprobada']
    list_filter = ['aprobada', 'calificacion', 'fecha']
    search_fields = ['usuario__username', 'producto__nombre', 'comentario']
    list_editable = ['aprobada']
    readonly_fields = ['fecha']

    fieldsets = (
        ('Información de la reseña', {
            'fields': ('usuario', 'producto', 'calificacion', 'comentario')
        }),
        ('Estado de la reseña', {
            'fields': ('aprobada', 'fecha')
        }),
    )

@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'red_social', 'calificacion', 'destacado', 'activo', 'fecha']
    list_filter = ['destacado', 'activo', 'red_social', 'calificacion', 'fecha']
    search_fields = ['nombre', 'comentario']
    list_editable = ['destacado', 'activo']
    readonly_fields = ['fecha']

    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre', 'imagen','red_social')
        }),
        ('Testimonio', {
            'fields': ('comentario', 'calificacion')
        }),
        ('Configuracion', {
            'fields': ('destacado', 'activo', 'fecha')
        }),
    )

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'session_key', 'total_items', 'total_precio', 'actualizado']
    list_filter = ['creado', 'actualizado']
    search_fields = ['usuario__username', 'session_key']
    inlines = [ItemCarritoInline]
    readonly_fields = ['creado', 'actualizado']

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'carrito', 'producto', 'cantidad', 'subtotal', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['producto__nombre', 'carrito__usuario__username']