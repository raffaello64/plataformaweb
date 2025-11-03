"""
En este módulo se enlazan las URL con las visualizaciones respectivas al ejecutarse.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard_docente/', views.dashboard_docente_view, name='dashboard_docente'),
    path('dashboard_estudiante/', views.dashboard_estudiante_view, name='dashboard_estudiante'),
    path('subir/', views.subir_documento_view, name='subir_documento'),
    path('eliminar/<int:documento_id>/', views.eliminar_documento_view, name='eliminar_documento'),
    path('descargar/<int:documento_id>/', views.descargar_documento_view, name='descargar_documento'),
]




