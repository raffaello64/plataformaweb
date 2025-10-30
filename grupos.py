import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TFG.settings')
django.setup()

from repositorio.models import Grupo

grupos = Grupo.objects.all()

if grupos.exists():
    print("✅ Grupos encontrados en la base de datos Render:")
    for g in grupos:
        print("-", g.nombre)
else:
    print("⚠️ No hay grupos en la base de datos Render.")
