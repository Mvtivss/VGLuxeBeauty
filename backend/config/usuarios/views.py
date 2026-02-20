from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import RegistroForm, LoginForm, PerfilForm, RecuperarPasswordForm
from .models import Perfil


def registro(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # El perfil se crea automáticamente por la señal
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """Vista personalizada de login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                
                # Redirigir a la página anterior o al home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


@login_required
def perfil(request):
    """Vista del perfil de usuario"""
    try:
        perfil_usuario = request.user.perfil
    except Perfil.DoesNotExist:
        # Crear perfil si no existe
        perfil_usuario = Perfil.objects.create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil_usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PerfilForm(instance=perfil_usuario)
    
    context = {
        'form': form,
        'perfil': perfil_usuario
    }
    
    return render(request, 'usuarios/perfil.html', context)


@login_required
def mis_pedidos(request):
    """Redirige al historial de pedidos"""
    return redirect('mis_pedidos')


class RecuperarPasswordView(PasswordResetView):
    """Vista para solicitar recuperación de contraseña"""
    template_name = 'usuarios/recuperar_password.html'
    email_template_name = 'usuarios/email/recuperar_password_email.html'
    subject_template_name = 'usuarios/email/recuperar_password_subject.txt'
    form_class = RecuperarPasswordForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(
            self.request,
            'Se han enviado las instrucciones para restablecer tu contraseña a tu correo electrónico.'
        )
        return super().form_valid(form)


class RecuperarPasswordConfirmView(PasswordResetConfirmView):
    """Vista para confirmar nueva contraseña"""
    template_name = 'usuarios/recuperar_password_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, 'Tu contraseña ha sido restablecida exitosamente.')
        return super().form_valid(form)
