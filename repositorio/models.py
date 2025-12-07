"""
En este módulo se establecen las estructuras principales.
Acá se encuentran los modelos de usuarios, documentos y grupos
y las correlaciones adentro del programa
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q  # Para consultas con OR en los mensajes


class Grupo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"


class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='documentos/')
    creado = models.DateTimeField(auto_now_add=True)
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documentos'
    )
    grupo = models.ForeignKey(
        'Grupo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documentos'
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"


class Perfil(models.Model):
    USUARIO_TIPO = (
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=USUARIO_TIPO)
    grupo = models.ForeignKey(Grupo, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


class MensajeQuerySet(models.QuerySet):
    """
    QuerySet personalizado para manejar visibilidad de mensajes.
    """

    def visibles_para(self, user):
        """
        Mensajes que el usuario puede ver, ya sea como remitente o destinatario,
        siempre que no los haya ocultado.
        """
        return self.filter(
            Q(remitente=user, oculto_para_remitente=False) |
            Q(destinatario=user, oculto_para_destinatario=False)
        )

    def enviados_por(self, user):
        """
        Mensajes enviados por el usuario que no ha ocultado.
        """
        return self.filter(
            remitente=user,
            oculto_para_remitente=False
        )

    def recibidos_por(self, user):
        """
        Mensajes recibidos por el usuario que no ha ocultado.
        """
        return self.filter(
            destinatario=user,
            oculto_para_destinatario=False
        )


class Mensaje(models.Model):
    remitente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos'
    )
    asunto = models.CharField(max_length=200)
    contenido = models.TextField()
    creado = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    # Este campo indica a qué mensaje concreto responde este mensaje
    respuesta_de = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='respuestas'
    )

    # Nuevos campos: ocultar para cada usuario sin borrar de la base de datos
    oculto_para_remitente = models.BooleanField(default=False)
    oculto_para_destinatario = models.BooleanField(default=False)

    # Manager con nuestro QuerySet personalizado
    objects = MensajeQuerySet.as_manager()

    def __str__(self):
        return f"{self.remitente.username} → {self.destinatario.username}: {self.asunto}"

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        # Si quisieras, podrías añadir un orden por defecto:
        # ordering = ['-creado']
