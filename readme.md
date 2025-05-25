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


**pour  créer an Account**

--python manage.py shell
--vous executer ça dans le shell
from Auth.models import Auth  


admin = Auth(
    username='admin',
    email='aya@gmail.com',
    first_name='aya',
    last_name='Touicha',
    phone_number='0987654321',
    address='Tetouan 93000',
    role='admin', #on peut creer aussi un manager
    is_staff=True, 
    is_superuser=True
)

admin.set_password('aya12345')  
admin.save() 

**Pour utiliser JWT 
    -- pip install PyJWT





