"""
En este módulo se establecen los formularios que se utilizan
en el repositorio web.

"""


from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo', 'grupo']
