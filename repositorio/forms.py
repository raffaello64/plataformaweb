"""
En este módulo se establecen los formularios que se utilizan
en el repositorio web.

"""


from django import forms
from .models import Documento, Perfil, Grupo


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo', 'grupo']


class PerfilForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.all().order_by('nombre'),
        required=False,
        label="Grupo"
    )

    class Meta:
        model = Perfil
        fields = ['user', 'tipo', 'grupo']

class UploadFileForm(forms.Form):
    archivo = forms.FileField(label="Seleccionar archivo CSV")
