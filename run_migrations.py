"""
Ejecuta automáticamente las migraciones de Django.
Solo debe usarse una vez al desplegar en Render.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TFG.settings')
django.setup()

from django.core.management import call_command

call_command('migrate')
print("✅ Migraciones ejecutadas correctamente en Render.")
