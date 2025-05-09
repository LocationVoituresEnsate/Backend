from django.db import models
from db_connection import db
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from bson import ObjectId  # en haut du fichier


# Si vous avez une collection MongoDB pour les voitures
voitures_collection = db['Voitures']

  

# Définir un gestionnaire personnalisé
