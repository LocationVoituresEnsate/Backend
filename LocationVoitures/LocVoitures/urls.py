from django.urls import path
from . import views
urlpatterns=[
   path("",views.index),
   path("add/",views.add_person),
   path("get/",views.get_all_person),

]