from django.urls import path
from . import views

urlpatterns = [
    path('livros/', views.lista_livros, name='lista'),
    path('novo/', views.novo_livro, name='novo'),
]