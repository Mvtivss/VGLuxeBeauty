from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'ciudad', 'pais', 'creado']
    list_filter = ['pais', 'recibir_newsletter', 'creado']
    search_fields = ['usuario__username', 'usuario__email', 'telefono', 'ciudad']
    readonly_fields = ['creado', 'actualizado']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Información Personal', {
            'fields': ('telefono', 'fecha_nacimiento', 'avatar')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion', 'ciudad', 'estado', 'codigo_postal', 'pais')
        }),
        ('Preferencias', {
            'fields': ('recibir_newsletter', 'recibir_notificaciones')
        }),
        ('Fechas', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )
