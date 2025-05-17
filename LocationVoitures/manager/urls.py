from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_manager, name='create_manager'),
    path('<str:user_id>/', views.get_manager, name='get_manager'),
    path('update/<str:user_id>/', views.update_manager, name='update_manager'),
    path('delete/<str:user_id>/', views.delete_manager, name='delete_manager'),
    path('', views.get_all_managers, name='get_all_managers'),
]
