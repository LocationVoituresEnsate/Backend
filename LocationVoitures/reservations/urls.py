from django.urls import path
from . import views

urlpatterns = [
    path('reservations/', views.create_reservation, name='create-reservation'),
    path('reservations/list/', views.list_reservations, name='list-reservations'),
    path('reservations/<str:reservation_id>/status/', 
         views.update_reservation_status, 
         name='update-reservation-status'),
]