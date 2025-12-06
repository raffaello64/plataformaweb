"""
En este módulo se enlazan las URL con las visualizaciones respectivas al ejecutarse.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_alt'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('dashboard_docente/', views.dashboard_docente_view, name='dashboard_docente'),
    path('dashboard_estudiante/', views.dashboard_estudiante_view, name='dashboard_estudiante'),

    # Documentos
    path('subir/', views.subir_documento_view, name='subir_documento'),
    path('eliminar/<int:documento_id>/', views.eliminar_documento_view, name='eliminar_documento'),
    path('descargar/<int:documento_id>/', views.descargar_documento_view, name='descargar_documento'),

    # ======================
    #   SISTEMA DE MENSAJES
    # ======================
    path('mensajes/', views.bandeja_entrada_view, name='bandeja_entrada'),
    path('mensajes/enviados/', views.mensajes_enviados_view, name='mensajes_enviados'),
    path('mensajes/nuevo/', views.redactar_mensaje_view, name='redactar_mensaje'),
    path('mensajes/<int:mensaje_id>/', views.detalle_mensaje_view, name='detalle_mensaje'),

    #URL para eliminar mensajes
    path('mensajes/eliminar/<int:mensaje_id>/', views.eliminar_mensaje_view, name='eliminar_mensaje'),
]
