"""
En este módulo se encuentra la lógica de la aplicación.
Se almacenan las vistas que procesan las solicitudes de los usuarios
y se generan las páginas correspondientes.
"""

from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.utils.crypto import get_random_string
import csv
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from .forms import DocumentoForm, UploadFileForm, MensajeForm
from .models import Documento, Perfil, Grupo, Mensaje


# Log in
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')

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
    if request.user.is_superuser:
        return redirect('/admin/')

    perfil = Perfil.objects.filter(user=request.user).first()

    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')

    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')

    documentos = Documento.objects.filter(docente=request.user).order_by('-creado')

    mensajes_no_leidos = Mensaje.objects.filter(
        destinatario=request.user,
        leido=False
    ).count()

    return render(request, 'repositorio/dashboard_docente.html', {
        'documentos': documentos,
        'perfil': perfil,
        'mensajes_no_leidos': mensajes_no_leidos,
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

    mensajes_no_leidos = Mensaje.objects.filter(
        destinatario=request.user,
        leido=False
    ).count()

    return render(request, 'repositorio/dashboard_estudiante.html', {
        'documentos': documentos,
        'grupo': grupo,
        'perfil': perfil,
        'mensajes_no_leidos': mensajes_no_leidos,
    })


# Subir archivos
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


# Eliminar archivos
@login_required
def eliminar_documento_view(request, documento_id):
    perfil = Perfil.objects.filter(user=request.user).first()

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

    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")
    return redirect('dashboard_docente')


# Descargar archivo
@login_required
def descargar_documento_view(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)

    if not documento.archivo:
        raise Http404("Archivo no encontrado")

    filename = os.path.basename(documento.archivo.name)

    response = FileResponse(
        documento.archivo.open('rb'),
        as_attachment=True,
        filename=filename,
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


# Importar datos desde csv para creación de credenciales
@user_passes_test(lambda u: u.is_superuser)
def importar_usuarios_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            reader = csv.DictReader(archivo.read().decode('utf-8').splitlines())

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=usuarios_creados.csv'

            writer = csv.writer(response)
            writer.writerow(['username', 'password', 'tipo', 'grupo'])

            for row in reader:
                username = row['username']
                tipo = row['tipo'].lower().strip()
                grupo_nombre = row.get('grupo', '').strip() or None

                if User.objects.filter(username=username).exists():
                    continue

                password = get_random_string(length=10)
                user = User.objects.create_user(username=username, password=password)

                grupo = None
                if grupo_nombre:
                    grupo, _ = Grupo.objects.get_or_create(nombre=grupo_nombre)

                Perfil.objects.create(user=user, tipo=tipo, grupo=grupo)
                writer.writerow([username, password, tipo, grupo_nombre])

            messages.success(
                request,
                "Usuarios importados correctamente. El archivo con credenciales se descargará automáticamente."
            )

            return response
    else:
        form = UploadFileForm()

    return render(request, 'repositorio/importar_usuarios.html', {'form': form})


# ==========================
#     SISTEMA DE MENSAJES
# ==========================

@login_required
def bandeja_entrada_view(request):
    mensajes = Mensaje.objects.filter(destinatario=request.user).order_by('-creado')
    return render(request, 'repositorio/mensajes/bandeja_entrada.html', {
        'mensajes': mensajes,
    })


@login_required
def mensajes_enviados_view(request):
    mensajes = Mensaje.objects.filter(remitente=request.user).order_by('-creado')
    return render(request, 'repositorio/mensajes/mensajes_enviados.html', {
        'mensajes': mensajes,
    })


@login_required
def redactar_mensaje_view(request):
    if request.method == 'POST':
        form = MensajeForm(request.POST, user=request.user)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.remitente = request.user

            respuesta_id = request.POST.get('respuesta_de')
            if respuesta_id:
                mensaje.respuesta_de = Mensaje.objects.filter(id=respuesta_id).first()

            mensaje.save()
            messages.success(request, "Mensaje enviado correctamente.")
            return redirect('bandeja_entrada')
    else:
        initial = {}
        respuesta_id = request.GET.get('respuesta_de')

        destinatario_id = request.GET.get('para')
        if destinatario_id:
            initial['destinatario'] = destinatario_id

        asunto_original = request.GET.get('asunto')
        if asunto_original:
            asunto_original = asunto_original.strip()
            if asunto_original.lower().startswith('re:'):
                initial['asunto'] = asunto_original
            else:
                initial['asunto'] = f"Re: {asunto_original}"

        form = MensajeForm(user=request.user, initial=initial)

    return render(request, 'repositorio/mensajes/redactar_mensaje.html', {
        'form': form,
        'respuesta_de_id': request.GET.get('respuesta_de', ''),
    })


@login_required
def detalle_mensaje_view(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)

    if mensaje.destinatario != request.user and mensaje.remitente != request.user:
        messages.error(request, "No tienes permiso para ver este mensaje.")
        return redirect('bandeja_entrada')

    if mensaje.destinatario == request.user and not mensaje.leido:
        mensaje.leido = True
        mensaje.save(update_fields=['leido'])

    if request.user == mensaje.destinatario:
        usuario_respuesta = mensaje.remitente
    else:
        usuario_respuesta = mensaje.destinatario

    perfil = Perfil.objects.filter(user=request.user).first()
    dashboard_url = None
    if perfil:
        if perfil.tipo == 'docente':
            dashboard_url = 'dashboard_docente'
        elif perfil.tipo == 'estudiante':
            dashboard_url = 'dashboard_estudiante'

    return render(request, 'repositorio/mensajes/mensaje_detalle.html', {
        'mensaje': mensaje,
        'usuario_respuesta': usuario_respuesta,
        'dashboard_url': dashboard_url,
    })


@login_required
def eliminar_mensaje_view(request, mensaje_id):
    """
    Permite eliminar un mensaje únicamente si el usuario es el remitente.
    """
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)

    if mensaje.remitente != request.user:
        messages.error(request, "Solo el remitente puede eliminar este mensaje.")
        return redirect('bandeja_entrada')

    mensaje.delete()
    messages.success(request, "Mensaje eliminado correctamente.")
    return redirect('mensajes_enviados')
