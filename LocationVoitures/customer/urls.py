from django.urls import path
from . import views

urlpatterns = [
    # 📊 Statistiques d'abord — doivent venir avant les routes dynamiques
    path('count/', views.total_clients, name='total_clients'),
    path('statistics/', views.clients_per_month, name='clients_per_month'),

    # ✏️ CRUD clients
    path('create/', views.create_client, name='create_client'),
    path('update/<str:client_id>/', views.update_client, name='update_client'),
    path('delete/<str:client_id>/', views.delete_client, name='delete_client'),
    path('<str:client_id>/', views.get_client, name='get_client'),  # ⚠️ route dynamique à placer en dernier
    path('', views.get_all_clients, name='get_all_clients'),
]
