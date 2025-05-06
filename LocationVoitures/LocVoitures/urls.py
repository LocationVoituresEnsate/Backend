from django.urls import path
from . import views
urlpatterns=[
   path("",views.index),
   path("add/",views.add_voiture),
   path("get/",views.get_all_voitures),
]