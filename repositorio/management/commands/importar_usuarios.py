"""
En este módulo se importan usuarios desde archivos CSV y
se crean usuarios y contraseñas automáticamente basado en los
nombres y apellidos. El usuario debe cambiar la contraseña
después de iniciar sesión y la opción de asignar el usuario
y contraseña manualmente sigue existiendo por parte del
superusuario

"""

import csv
import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from repositorio.models import Perfil, Grupo


class Command(BaseCommand):
    help = 'Importa usuarios (docentes y estudiantes) desde un archivo CSV y genera contraseñas automáticas.'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str, help='Ruta al archivo CSV con los usuarios.')

    def handle(self, *args, **kwargs):
        ruta_csv = kwargs['archivo_csv']
        usuarios_creados = []

        with open(ruta_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for fila in reader:
                nombre = fila['nombre'].strip()
                apellido = fila['apellido'].strip()
                tipo = fila['tipo'].strip().lower()
                grupo_nombre = fila.get('grupo', '').strip()

                username = f"{nombre[0].lower()}.{apellido.lower()}"

                caracteres = string.ascii_letters + string.digits + "!@#$%^&*()"
                password = ''.join(random.choice(caracteres) for _ in range(8))

                grupo = None
                if grupo_nombre:
                    grupo, _ = Grupo.objects.get_or_create(nombre=grupo_nombre)

                user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={'first_name': nombre, 'last_name': apellido}
                )
                user.set_password(password)
                user.save()

                Perfil.objects.update_or_create(
                    user=user,
                    defaults={'tipo': tipo, 'grupo': grupo}
                )

                usuarios_creados.append({
                    'nombre': nombre,
                    'apellido': apellido,
                    'usuario': username,
                    'tipo': tipo,
                    'grupo': grupo_nombre,
                    'contraseña': password
                })

                self.stdout.write(f"{username} ({tipo}) creado correctamente - Contraseña: {password}")

        with open('usuarios_creados.csv', 'w', newline='', encoding='utf-8') as f_out:
            campos = ['nombre', 'apellido', 'usuario', 'tipo', 'grupo', 'contraseña']
            writer = csv.DictWriter(f_out, fieldnames=campos)
            writer.writeheader()
            writer.writerows(usuarios_creados)

        self.stdout.write("Todos los usuarios fueron creados y guardados en 'usuarios_creados.csv'.")
