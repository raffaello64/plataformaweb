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
        user = kwargs.pop('user', None)  # usuario logueado
        super().__init__(*args, **kwargs)

        # Si no hay usuario o no hay perfil → no mostrar destinatarios
        if user is None:
            self.fields['destinatario'].queryset = User.objects.none()
            return

        perfil = Perfil.objects.filter(user=user).first()

        if perfil is None or perfil.grupo is None:
            self.fields['destinatario'].queryset = User.objects.none()
            return

        grupo = perfil.grupo

        # DOCENTE → puede escribir a ESTUDIANTES del mismo grupo
        if perfil.tipo == 'docente':
            self.fields['destinatario'].queryset = User.objects.filter(
                perfil__grupo=grupo,
                perfil__tipo='estudiante'
            ).order_by('username')

        # ESTUDIANTE → puede escribir a DOCENTES del mismo grupo
        elif perfil.tipo == 'estudiante':
            self.fields['destinatario'].queryset = User.objects.filter(
                perfil__grupo=grupo,
                perfil__tipo='docente'
            ).order_by('username')

        # Por seguridad
        else:
            self.fields['destinatario'].queryset = User.objects.none()
