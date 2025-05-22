from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from bson import ObjectId
from django.utils import timezone

def generate_objectid():
    # Génère un ObjectId en string 24 caractères hexadécimaux
    return str(ObjectId())

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email doit être renseigné.')
        email = self.normalize_email(email)
        print(f"Normalized email: {email}")

        if self.model.objects.filter(email=email).exists():
            print("Email already exists")  # Debug
            raise ValueError('Cet email est déjà utilisé.')

        user = self.model(username=username, email=email, **extra_fields)
        print(f"User model created: {user}")  # Debug
        user.set_password(password)
        print("Password set")  # Debug

        # Ici on s'assure que last_login n'est pas None
        if not user.last_login:
            user.last_login = timezone.now()

        user.save(using=self._db)
        print("User saved successfully")  # Debug
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, max_length=24, default=generate_objectid, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('manager', 'Manager')], default='manager')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        related_name='manager_users',
        blank=True,
        help_text='Les groupes auxquels cet utilisateur appartient.',
        verbose_name='groupes'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='manager_user_permissions',
        blank=True,
        help_text='Permissions spécifiques accordées à cet utilisateur.',
        verbose_name='permissions utilisateur'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'Auth'  # Nom collection MongoDB

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
      if self.last_login is None:
          self.last_login = timezone.now()  # ou simplement ne pas l’inclure à l’insert

      # Synchroniser is_staff et is_superuser selon le rôle
      if self.role == 'admin':
          self.is_staff = True
          self.is_superuser = True
      else:
          self.is_staff = False
          self.is_superuser = False

      super().save(*args, **kwargs)

