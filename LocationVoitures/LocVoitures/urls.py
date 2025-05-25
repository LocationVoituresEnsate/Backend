from django.urls import path
from . import views
urlpatterns=[
   path("",views.index),
   path("add/",views.add_voiture),
   path("get/",views.get_all_voitures),
   path('count/',views.count_voitures, name='count_voitures'),
   path("update/<str:voiture_id>/",views.update_voiture),
   path('delete/<str:voiture_id>/',views.delete_voiture),
]