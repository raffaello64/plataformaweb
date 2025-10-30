import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TFG.settings')
django.setup()

from django.core.management import call_command

print("🚀 Iniciando migraciones en Render...")
call_command('makemigrations', 'repositorio')
call_command('migrate')
print("✅ Migraciones completadas correctamente.")
