"""
Acá se ingresan los modelos al panel que administra el superusuario.
"""

from django.contrib import admin
from .models import Perfil, Documento, Grupo

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'grupo')
    search_fields = ('user__username', 'tipo')
    list_filter = ('tipo', 'grupo')
    # 🔹 Mostramos todos los grupos disponibles en un desplegable normal
    raw_id_fields = ()  # Nos aseguramos de no usar IDs
    autocomplete_fields = ()  # Desactivamos el buscador
    fields = ('user', 'tipo', 'grupo')  # Forzamos que 'grupo' sea visible

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')
