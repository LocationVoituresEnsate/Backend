from django.urls import path
from . import views
from .views import total_revenu


urlpatterns = [
    # CRUD Réservations
    path('add/', views.create_reservation, name='create-reservation'),
    path('statistics/', views.reservations_per_month_status, name='reservations_stats'),
    path('revenu-par-annee/', total_revenu, name='revenu_par_annee'),
    path('get/<str:reservation_id>/', views.get_reservation, name='get-reservation'),
    path('get/', views.get_all_reservations, name='get-all-reservations'),
    path('accept_reservation/<str:reservation_id>', views.accept_reservation),
    path('decline_reservation/<str:reservation_id>', views.decline_reservation),
     path('pending-count/', views.count_pending_reservations, name='count_pending_reservations'),
]