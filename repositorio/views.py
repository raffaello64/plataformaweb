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


# --- LOGIN ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            perfil = Perfil.objects.filter(user=user).first()

            # 🔧 Si el usuario no tiene perfil, lo mandamos al admin
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


# --- LOGOUT ---
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# --- DASHBOARD DOCENTE ---
@login_required
def dashboard_docente_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()

    # 🔧 Si no tiene perfil, redirigimos al admin
    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')

    # 🔧 Si no es docente, lo mandamos al dashboard del estudiante
    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')

    documentos = Documento.objects.filter(docente=request.user).order_by('-creado')
    return render(request, 'repositorio/dashboard_docente.html', {
        'documentos': documentos,
        'perfil': perfil
    })


# --- DASHBOARD ESTUDIANTE ---
@login_required
def dashboard_estudiante_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()

    # 🔧 Si no tiene perfil, redirigir al admin
    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')

    # 🔧 Si es docente, redirigir al dashboard docente
    if perfil.tipo == 'docente':
        return redirect('dashboard_docente')

    grupo = perfil.grupo if perfil else None
    documentos = Documento.objects.filter(grupo=grupo).order_by('-creado') if grupo else Documento.objects.none()

    return render(request, 'repositorio/dashboard_estudiante.html', {
        'documentos': documentos,
        'grupo': grupo,
        'perfil': perfil
    })


# --- SUBIR DOCUMENTO (solo docente) ---
@login_required
def subir_documento_view(request):
    perfil = Perfil.objects.filter(user=request.user).first()

    # 🔧 Si no tiene perfil, redirigir al admin
    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')

    # 🔧 Si no es docente, no puede subir documentos
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
# --- ELIMINAR DOCUMENTO (solo docente) ---
@login_required
def eliminar_documento_view(request, documento_id):
    perfil = Perfil.objects.filter(user=request.user).first()

    # Validar que tenga perfil y sea docente
    if not perfil:
        messages.warning(request, "Tu cuenta no tiene un perfil asignado.")
        return redirect('/admin/')
    if perfil.tipo != 'docente':
        return redirect('dashboard_estudiante')

    # Buscar documento
    try:
        documento = Documento.objects.get(id=documento_id, docente=request.user)
    except Documento.DoesNotExist:
        messages.error(request, "No se encontró el documento o no tienes permiso para eliminarlo.")
        return redirect('dashboard_docente')

    # Eliminar documento
    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")
    return redirect('dashboard_docente')
