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
    autocomplete_fields = ('grupo',)  # 🔹 Permite elegir grupos existentes

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')
