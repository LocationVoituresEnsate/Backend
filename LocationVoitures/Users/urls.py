from django.urls import path
from . import views
urlpatterns=[
   path('register/', views.register, name='register'),
   path('login/', views.login, name='login'),
   
  path('manager/create/', views.create_manager, name='create_manager'),
  path('manager/<str:manager_id>/', views.get_manager, name='get_manager'),
  path('manager/update/<str:manager_id>/', views.update_manager, name='update_manager'),
  path('manager/delete/<str:manager_id>/', views.delete_manager, name='delete_manager'),
  path('managers/', views.get_all_managers, name='get_all_managers'),  # Nouvelle route

]