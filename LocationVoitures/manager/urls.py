from django.urls import path
from .views import create_manager_view,get_all_managers,delete_manager,update_manager

urlpatterns = [
    path('create/', create_manager_view, name='create_manager_view'),
    path('', get_all_managers, name='get_all_managers'),
    path('delete/<str:manager_id>/', delete_manager, name='delete_manager'),
    path('update/<str:manager_id>/', update_manager, name='update_manager'),
]
