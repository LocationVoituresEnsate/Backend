# models.py
from django.db import models

class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    license_number = models.CharField(max_length=20, blank=True, null=True)  # Permis de conduire
    license_country = models.CharField(max_length=50, blank=True, null=True)  # Pays du permis
    rented_vehicles = models.JSONField(blank=True, null=True)  # Liste des voitures réservées (IDs des véhicules)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
