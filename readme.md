--python should be installed
Django installation:
--pip install django
Pymongo installation
--pip install pymongo
Database setup
--our unified name is LocationVoitures
--check that the connection url in 'db_connection.py' is correct from mongodb compass
-- we should create the database before starting the development
Running the project:
-- cd LocationVoitures
-- python manage.py runserver


**pour  créer an AdminAccount**

--python manage.py shell
--vous executer ça dans le shell

from django.contrib.auth import get_user_model
User = get_user_model()

User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='admin',
    first_name='Super',
    last_name='User',
    phone_number='0987654321',
    address='Tetouan 93000'
)



