from django.urls import path
from . import views
from .views import total_revenu,reservations_count_per_day


urlpatterns = [
    # CRUD Réservations
    path('add/', views.create_reservation, name='create-reservation'),
    path('statistics/', views.reservations_per_month_status, name='reservations_stats'),
    path('revenu-par-annee/', total_revenu, name='revenu_par_annee'),
    path('revenu_mensuel/', views.revenu_mensuel, name='revenu_mensuel'),
    path('count-per-day/', reservations_count_per_day, name='reservations_count_per_day'),
    path('get/<str:reservation_id>/', views.get_reservation, name='get-reservation'),
    path('get/', views.get_all_reservations, name='get-all-reservations'),
    path('accept_reservation/<str:reservation_id>', views.accept_reservation),
    path('decline_reservation/<str:reservation_id>', views.decline_reservation),
     path('pending-count/', views.count_pending_reservations, name='count_pending_reservations'),
     path('count-by-voiture/', views.reservations_count_by_voiture, name='reservations_count_by_voiture'),
     path('top-vehicles/', views.top_reserved_vehicles, name='top_reserved_vehicles'),
     path('recent/', views.recent_reservations, name='recent_reservations')
]