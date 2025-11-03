"""
Acá se ingresan los modelos al panel que administra el superusuario.
"""
from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.response import TemplateResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Perfil, Documento, Grupo


# --- Ocultar modelo Group del panel ---
admin.site.unregister(Group)


# --- Configuración de los modelos del sistema ---
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'grupo':
            kwargs["queryset"] = Grupo.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')


# --- Vista personalizada del admin para mostrar tu sitio_base ---
def sitio_base_admin_view(request):
    """
    Vista que renderiza la plantilla 'admin/sitio_base.html'
    dentro del contexto del panel de administración.
    """
    context = admin.site.each_context(request)
    return TemplateResponse(request, "admin/sitio_base.html", context)
