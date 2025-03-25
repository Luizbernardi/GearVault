from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth, messages
# Create your views here.


def login(request):
    if request.method == "POST":

        usuario = request.POST['usuario']
        senha = request.POST['senha']

        verificar_usuario = auth.authenticate(username=usuario, password=senha)

        if verificar_usuario != None:
            auth.login(request, verificar_usuario)

            return redirect('home')

        else:
            return render(request, 'login.html', {'error_message': "Usuário ou senha inválidos"})

    return render(request, 'pages/login.html')


def logout(request):
    auth.logout(request)
    return redirect('home')


def register(request):
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not usuario or not email or not senha or not confirmar_senha:
            return render(request, 'pages/register.html', {'error_message': "Todos os campos são obrigatórios."})

        if senha != confirmar_senha:
            return render(request, 'pages/register.html', {'error_message': "As senhas não coincidem."})

        try:
            User.objects.create_user(
                username=usuario, email=email, password=senha)
            return redirect('login')
        except Exception as e:
            return render(request, 'pages/register.html', {'error_message': f"Erro ao registrar: {str(e)}"})
    else:
        return render(request, 'pages/register.html')
