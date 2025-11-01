"""
Rutas del proyecto TFG.
Aquí incluimos las URLs principales: la parte de administración,
las rutas de nuestra app repositorio y las vistas de cambio de contraseñas.
También se encuentra la configuración para que funcionen los archivos estáticos y archivos subidos.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),

    # App principal
    path('', include('repositorio.urls')),

    # Cambio de contraseña
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='repositorio/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='repositorio/password_change_done.html'
    ), name='password_change_done'),
]

# Archivos estáticos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
