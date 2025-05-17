from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from bson import ObjectId  # en haut du fichier
from db_connection import db
# Si vous avez une collection MongoDB pour les users
user_collection = db['Users']

# Définir un gestionnaire personnalisé
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email doit être renseigné.')
        
        # Vérifier si l'email existe déjà dans la base de données
        if self.model.objects.filter(email=email).exists():
            raise ValueError('Cet email est déjà utilisé.')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hachage du mot de passe
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return self.create_user(username, email, password, **extra_fields)

# Fonction pour générer l'ObjectId
def generate_objectid():
    return str(ObjectId())

# Modèle d'utilisateur personnalisé
class User(AbstractBaseUser):
    id = models.CharField(primary_key=True, max_length=24, default=generate_objectid, editable=False)  # Remplacer lambda par la fonction generate_objectid
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('manager', 'Manager')], default='manager')
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
