"""
En este módulo se importan usuarios desde archivos CSV y
se crean usuarios y contraseñas automáticamente basado en los
nombres y apellidos. El usuario debe cambiar la contraseña
después de iniciar sesión y la opción de asignar el usuario
y contraseña manualmente sigue existiendo por parte del
superusuario.
Se crea un archivo CSV con los nuevos usuarios y contraseñas
y la respectiva asignación de grupos

"""

import csv
import random
import string
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from repositorio.models import Perfil, Grupo


class Command(BaseCommand):
    help = 'Importación de usuarios desde archivos CSV para creación de contraseñas y asignación de grupos.'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str, help='Ruta de archivo CSV.')

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

                # Generación aleatoria de usuario y password para posterior cambio por parte del usuario
                username = f"{nombre[0].lower()}.{apellido.lower()}"
                caracteres = string.ascii_letters + string.digits + "!@#$%^&*()"
                password = ''.join(random.choice(caracteres) for _ in range(8))

                # Asignación o creación de grupo
                grupo = None
                if grupo_nombre:
                    grupo, _ = Grupo.objects.get_or_create(nombre=grupo_nombre)

                # Creación de usuario
                user, creado = User.objects.get_or_create(
                    username=username,
                    defaults={'first_name': nombre, 'last_name': apellido}
                )

                if creado:
                    user.set_password(password)
                    user.save()
                    contrasena_guardar = password
                else:
                    contrasena_guardar = '(ya existía)'

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
                    'contraseña': contrasena_guardar
                })

                self.stdout.write(f"{username} ({tipo}) procesado correctamente.")

        # Almacenamiento de usuario y contraseña creada en CSV con fecha
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"usuarios_creados_{timestamp}.csv"


        with open(archivo_salida, 'w', newline='', encoding='utf-8') as f_out:
            campos = ['nombre', 'apellido', 'usuario', 'tipo', 'grupo', 'contraseña']
            writer = csv.DictWriter(f_out, fieldnames=campos)
            writer.writeheader()
            writer.writerows(usuarios_creados)

        self.stdout.write(self.style.SUCCESS(f"Usuarios almacenados en '{archivo_salida}'"))
