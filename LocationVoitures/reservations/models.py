from django.db import models
from db_connection import db

reservations = db['Reservations']
clients = db['client']
voitures = db['Voitures']