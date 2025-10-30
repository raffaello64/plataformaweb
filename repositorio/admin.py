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
    # 🔹 Asegura que 'grupo' se muestre como desplegable
    fields = ('user', 'tipo', 'grupo')
    ordering = ('user',)
    # 🔹 Forzamos a Django a cargar todos los grupos existentes
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'grupo':
            kwargs["queryset"] = Grupo.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')
