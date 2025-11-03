"""
En este módulo se encuentra la lógica de la aplicación.
Se almacenan las vistas que procesan las solicitudes de los usuarios
y se generan las páginas correspondientes.
"""


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import DocumentoForm
from .models import Documento, Perfil
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
import os


# --- LOGIN ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            perfil = Perfil.objects.filter(user=user).first()


            if not perfil:
                messages.warning(request, "No tienes un perfil asignado. Accede al panel de administración.")
                return redirect('/admin/')

            if perfil.tipo == 'docente':
                return redirect('dashboard_docente')
            else:
                return redirect('dashboard_estudiante')
        else:
            return render(request, 'repositorio/login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'repositorio/login.html')


# Cerrar sesión
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# Página de inicio del docente
@login_required
def dashboard_docente_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()


    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')


    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')

    documentos = Documento.objects.filter(docente=request.user).order_by('-creado')
    return render(request, 'repositorio/dashboard_docente.html', {
        'documentos': documentos,
        'perfil': perfil
    })


# Página de inicio del estudiante
@login_required
def dashboard_estudiante_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()


    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')


    if perfil.tipo == 'docente':
        return redirect('dashboard_docente')

    grupo = perfil.grupo if perfil else None
    documentos = Documento.objects.filter(grupo=grupo).order_by('-creado') if grupo else Documento.objects.none()

    return render(request, 'repositorio/dashboard_estudiante.html', {
        'documentos': documentos,
        'grupo': grupo,
        'perfil': perfil
    })


# Subida de documentos por parte del docente
@login_required
def subir_documento_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()


    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')


    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.docente = request.user
            doc.save()
            messages.success(request, "Documento subido correctamente.")
            return redirect('dashboard_docente')
    else:
        form = DocumentoForm()

    return render(request, 'repositorio/subir_documento.html', {'form': form, 'perfil': perfil})
# Eliminar documentos
@login_required
def eliminar_documento_view(request, documento_id):
    perfil = Perfil.objects.filter(user=request.user).first()

    # verificación de perfil
    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')
    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')


    try:
        documento = Documento.objects.get(id=documento_id, docente=request.user)
    except Documento.DoesNotExist:
        messages.error(request, "No se encontró el documento o no tienes permiso para eliminarlo.")
        return redirect('dashboard_docente')

    # Eliminar documento
    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")
    return redirect('dashboard_docente')

@login_required
def descargar_documento_view(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)

    if not documento.archivo:
        raise Http404("Archivo no encontrado")

    # Obtener nombre limpio del archivo
    filename = os.path.basename(documento.archivo.name)

    # Forzar encabezados de descarga
    response = FileResponse(
        documento.archivo.open('rb'),
        as_attachment=True,
        filename=filename,
        content_type='application/octet-stream'  # Fuerza descarga en móviles
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response