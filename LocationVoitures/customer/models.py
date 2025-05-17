from db_connection import db  # ta connexion pymongo déjà configurée
from bson import ObjectId
from datetime import datetime


class Client:
    def __init__(self, first_name, last_name, email, phone_number=None,
                 address=None, license_number=None, license_country=None,
                 rented_vehicles=None, date_joined=None, _id=None):
        self._id = _id or ObjectId()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.license_number = license_number
        self.license_country = license_country
        self.rented_vehicles = rented_vehicles or []
        self.date_joined = date_joined or datetime.utcnow()

    @staticmethod
    def collection():
        return db['client']

    def save(self):
        data = self.__dict__.copy()
        data['_id'] = self._id
        Client.collection().replace_one({'_id': self._id}, data, upsert=True)

    @staticmethod
    def find_by_email(email):
        data = Client.collection().find_one({'email': email})
        if data:
            return Client(**data)
        return None

    @staticmethod
    def find_all():
        return [Client(**doc) for doc in Client.collection().find()]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
