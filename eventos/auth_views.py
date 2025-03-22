from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def custom_logout(request):
    """
    View personalizada para realizar o logout do usuário.
    Funciona com qualquer método HTTP (GET ou POST).
    """
    logout(request)
    messages.success(request, "Você saiu do sistema com sucesso.")
    return redirect('login')
