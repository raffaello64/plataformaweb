"""
Acá se ingresan los modelos al panel que administra el superusuario.
"""

from django.contrib import admin
from .models import Perfil, Documento, Grupo

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'grupo')
    list_filter = ('tipo', 'grupo')
    search_fields = ('user__username',)

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    list_filter = ('grupo', 'docente')
    search_fields = ('titulo',)
