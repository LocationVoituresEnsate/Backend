from db_connection import db
from bson import ObjectId
from datetime import datetime


class Manager:
    def __init__(self, username, email, password, first_name, last_name,
                 phone_number=None, address=None, role='manager',
                 date_joined=None, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.address = address
        self.role = role
        self.date_joined = date_joined or datetime.utcnow()
        # Ignorer les autres champs inconnus passés dans kwargs (ex: last_login)

    @staticmethod
    def collection(collection_name='Auth'):
        return db[collection_name]

    def save(self, collection_name='Auth'):
        data = self.__dict__.copy()
        data['_id'] = self._id
        Manager.collection(collection_name).replace_one({'_id': self._id}, data, upsert=True)

    @staticmethod
    def find_by_email(email, collection_name='Auth'):
        data = Manager.collection(collection_name).find_one({'email': email})
        if data:
            return Manager(**data)
        return None

    @staticmethod
    def find_all(collection_name='Auth'):
        return [Manager(**doc) for doc in Manager.collection(collection_name).find()]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    @staticmethod
    def update_manager(manager_id, update_data, collection_name='Auth'):
      """
      Met à jour un manager identifié par manager_id avec les champs dans update_data.
      Retourne True si modification, False sinon.
      """
      from bson import ObjectId

      try:
          obj_id = ObjectId(manager_id)
      except Exception:
          raise ValueError("ID invalide")

      if '_id' in update_data:
          update_data.pop('_id')

      result = Manager.collection(collection_name).update_one(
          {'_id': obj_id},
          {'$set': update_data}
      )
      return result.modified_count > 0
    
    @staticmethod
    def find_by_email_exclude_id(email, exclude_id=None, collection_name='Auth'):
        query = {'email': email}
        if exclude_id:
            try:
                oid = ObjectId(exclude_id)
                query['_id'] = {'$ne': oid}
            except Exception:
                pass  # ignore si id invalide
        data = Manager.collection(collection_name).find_one(query)
        if data:
            return Manager(**data)
        return None
    
    @staticmethod
    def update_manager(manager_id, update_data, collection_name='Auth'):
        from bson import ObjectId

        try:
            obj_id = ObjectId(manager_id)
        except Exception:
            raise ValueError("ID invalide")

        # Debug print pour voir update_data
        print(f"Update manager {manager_id} avec données: {update_data}")

        result = Manager.collection(collection_name).update_one(
            {'_id': obj_id},
            {'$set': update_data}
        )
        return result.modified_count > 0



