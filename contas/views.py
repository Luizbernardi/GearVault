from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from contas.models import Profile



def login(request):
    if request.user.is_authenticated:
        # Usuário já está logado, pode redirecionar conforme a role.
        role = request.user.profile.role
        if role == 'USUARIO':
            return redirect('dashboard_usuario')
        elif role == 'ADMIN':
            return redirect('dashboard_admin')

    if request.method == "POST":
        usuario = request.POST['usuario']
        senha = request.POST['senha']
        verificar_usuario = auth.authenticate(username=usuario, password=senha)

        if verificar_usuario is not None:
            auth.login(request, verificar_usuario)

            role = verificar_usuario.profile.role
            if role == 'USUARIO':
                return redirect('dashboard_usuario')
            elif role == 'ADMIN':
                return redirect('dashboard_admin')
            else:
                return render(request, 'login.html', {'error_message': "Perfil sem role definida."})
        else:
            return render(request, 'login.html', {'error_message': "Usuário ou senha inválidos"})
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def register(request):
    if request.user.is_authenticated:
        role = request.user.profile.role
        if role == 'USUARIO':
            return redirect('dashboard_usuario')
        elif role == 'ADMIN':
            return redirect('dashboard_admin')

    if request.method == "POST":
        usuario = request.POST.get('username') 
        email = request.POST.get('email')
        senha = request.POST.get('password')
        confirmar_senha = request.POST.get('password_confirm')
        role = request.POST.get('role')

        if not usuario or not email or not senha or not confirmar_senha or not role:
            return render(request, 'register.html', {'error_message': "Todos os campos são obrigatórios."})

        if senha != confirmar_senha:
            return render(request, 'register.html', {'error_message': "As senhas não coincidem."})

        try:
            novo_usuario = User.objects.create_user(username=usuario, email=email, password=senha)
            
            profile = Profile.objects.get(user=novo_usuario)
            profile.role = role
            profile.save()

            return redirect('login')
        except Exception as e:
            return render(request, 'register.html', {'error_message': f"Erro ao registrar: {str(e)}"})
    else:   
        return render(request, 'register.html')