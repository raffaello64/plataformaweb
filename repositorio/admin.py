"""
Acá se ingresan los modelos al panel que administra el superusuario.
"""

from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from .models import Perfil, Documento, Grupo


# Se oculta la sección de grupos
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'grupo':
            kwargs["queryset"] = Grupo.objects.all().order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'grupo', 'creado')
    search_fields = ('titulo', 'docente__username')
    list_filter = ('grupo', 'creado')


# Enlace a importar usuarios desde la pagina de superusuario
class ImportarUsuariosAdmin(admin.ModelAdmin):
    change_list_template = "admin/importar_datos_enlace.html"

    def changelist_view(self, request, extra_context=None):
        # lleva a la sección importar usuarios
        return HttpResponseRedirect(reverse('importar_usuarios'))



admin.site.register(type('ImportarUsuarios', (), {}), ImportarUsuariosAdmin)
