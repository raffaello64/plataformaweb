"""
En este módulo se establecen los formularios que se utilizan
en el repositorio web.
"""

from django import forms
from django.contrib.auth.models import User

from .models import Documento, Perfil, Grupo, Mensaje


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


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['destinatario', 'asunto', 'contenido']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields['destinatario'].queryset = User.objects.none()
            return

        perfil = Perfil.objects.filter(user=user).first()

        if perfil is None or perfil.grupo is None:
            self.fields['destinatario'].queryset = User.objects.none()
            return

        grupo = perfil.grupo

        # Docente → puede escribir a estudiantes del mismo grupo
        if perfil.tipo == 'docente':
            self.fields['destinatario'].queryset = User.objects.filter(
                perfil__grupo=grupo,
                perfil__tipo='estudiante'
            ).order_by('username')

        # Estudiante → puede escribir a docentes del mismo grupo
        elif perfil.tipo == 'estudiante':
            self.fields['destinatario'].queryset = User.objects.filter(
                perfil__grupo=grupo,
                perfil__tipo='docente'
            ).order_by('username')

        else:
            self.fields['destinatario'].queryset = User.objects.none()

    def clean_asunto(self):
        asunto = self.cleaned_data.get("asunto", "")
        return asunto.strip()
