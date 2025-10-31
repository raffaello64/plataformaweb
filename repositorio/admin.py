"""
Acá se ingresan los modelos al panel que administra el superusuario.
"""

from django.contrib import admin
from django.contrib.auth.models import Group  # 👈 Importa el modelo de grupos del sistema
from .models import Perfil, Documento, Grupo


# 🔹 Ocultar el modelo Group del panel de administración (los grupos del sistema de Django)
admin.site.unregister(Group)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'grupo')
    search_fields = ('user__username', 'tipo')
    list_filter = ('tipo', 'grupo')
    fields = ('user', 'tipo', 'grupo')
    ordering = ('user',)

    # Forzar que Django cargue todos los grupos en el desplegable (ordenados alfabéticamente)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'grupo':
            kwargs["queryset"] = Grupo.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')
