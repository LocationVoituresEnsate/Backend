from db_connection import db
from bson import ObjectId
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password as django_check_password

class Auth:
    def __init__(self, username, email, password=None, first_name='', last_name='',
                 role='manager', phone_number=None, address=None,
                 is_staff=False, is_superuser=False, date_joined=None, _id=None):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password = password  # hash stocké ici (format Django)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.phone_number = phone_number
        self.address = address
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.date_joined = date_joined or datetime.utcnow()

    @staticmethod
    def collection():
        return db['Auth']  # nom exact de la collection MongoDB

    def save(self):
        data = self.__dict__.copy()
        data['_id'] = self._id
        Auth.collection().replace_one({'_id': self._id}, data, upsert=True)

    @staticmethod
    def find_by_email(email):
        data = Auth.collection().find_one({'email': email})
        if data:
            allowed_keys = {'_id', 'username', 'email', 'password', 'first_name', 'last_name',
                            'role', 'phone_number', 'address', 'is_staff', 'is_superuser', 'date_joined'}
            filtered_data = {k: v for k, v in data.items() if k in allowed_keys}
            return Auth(**filtered_data)
        return None

    @staticmethod
    def find_all():
        allowed_keys = {'_id', 'username', 'email', 'password', 'first_name', 'last_name',
                        'role', 'phone_number', 'address', 'is_staff', 'is_superuser', 'date_joined'}
        return [
            Auth(**{k: v for k, v in doc.items() if k in allowed_keys})
            for doc in Auth.collection().find()
        ]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, plain_password):
        if not self.password:
            return False
        return django_check_password(plain_password, self.password)

    def __str__(self):
        return self.email

def generate_objectid():
    return str(ObjectId())
