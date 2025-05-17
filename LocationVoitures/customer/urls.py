from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_client, name='create_client'),
    path('<str:client_id>/', views.get_client, name='get_client'),
    path('update/<str:client_id>/', views.update_client, name='update_client'),
    path('delete/<str:client_id>/', views.delete_client, name='delete_client'),
    path('', views.get_all_clients, name='get_all_clients'),  # Route pour récupérer tous les clients

]
