from django.shortcuts import render


def home(request):
    """
    Página inicial do projeto.
    Exibe um dashboard com links para os principais apps.
    """
    return render(request, 'home.html', {
        'title': 'Bem-vindo ao Capinha!',
    })


def sobre(request):
    """
    Página institucional explicando o projeto Capinha.
    """
    return render(request, 'sobre.html', {
        'title': 'Sobre o Projeto - Capinha',
    })


def como_testar(request):
    """
    Página com orientações passo a passo para testar o sistema.
    """
    return render(request, 'como_testar.html', {
        'title': 'Como Testar o Sistema - Capinha',
    })
