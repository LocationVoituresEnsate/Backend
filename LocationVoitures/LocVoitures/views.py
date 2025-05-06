import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse, redirect
from .models import voitures_collection
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import authenticate, login


# Create your views here.
def home(request):
    return render(request,"home.html")
def index(request):
    return HttpResponse("app is running ...")

@csrf_exempt
def add_voiture(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            voiture_data = {
                "brand": data.get('brand', ''),
                "model": data.get('model', ''),
                "year": int(data.get('year', 0)),
                "registrationNumber": data.get('registrationNumber', ''),
                "color": data.get('color', ''),
                "dailyPrice": float(data.get('dailyPrice', 0)),
                "available": True,
                "createdAt": datetime.datetime.now(),
                "updatedAt": datetime.datetime.now()
            }

            voitures_collection.insert_one(voiture_data)
            return JsonResponse({"message": "Voiture ajoutée avec succès"}, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def get_all_voitures(request):
    voitures=voitures_collection.find()
    return HttpResponse(voitures)
  




@csrf_exempt  # Désactive la protection CSRF pour les tests via API
def register(request):
    if request.method == 'POST':
        try:
            # Utiliser json.loads() pour charger les données JSON depuis request.body
            data = json.loads(request.body)
            
            # Extraire les données nécessaires
            username = data.get("username")
            password = data.get("password")
            email = data.get("email")
            role = data.get("role")  # Rôle de l'utilisateur (admin ou manager)
            first_name = data.get("first_name")  # Prénom
            last_name = data.get("last_name")    # Nom
            phone_number = data.get("phone_number")  # Numéro de téléphone
            address = data.get("address")  # Adresse
            
            # Vérifier que les champs obligatoires sont fournis
            if not username or not password or not email:
                return JsonResponse({
                    'message': 'Les champs username, password, et email sont obligatoires.',
                    'error': True
                }, status=400)
            
            # Vérifier si l'email est déjà utilisé
            if get_user_model().objects.filter(email=email).exists():
                return JsonResponse({
                    'message': 'Cet email est déjà utilisé.',
                    'error': True
                }, status=400)

            # Créer l'utilisateur
            user = get_user_model().objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                password=password,  # Assurez-vous que le mot de passe est haché
                role=role  # Ajouter le rôle
            )

            # Convertir l'ObjectId en chaîne pour le renvoyer dans la réponse
            user_id = str(user.id)  # MongoDB retourne un ObjectId, converti en chaîne

            # Retourner une réponse JSON avec les informations de l'utilisateur créé
            return JsonResponse({
                'message': 'Utilisateur créé avec succès!',
                'user_id': user_id,  # Utiliser l'ID converti en chaîne
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'address': user.address,
            }, status=201)

        except Exception as e:
            return JsonResponse({
                'message': f'Erreur lors de la création de l\'utilisateur : {str(e)}',
                'error': True
            }, status=500)

    return JsonResponse({
        'message': 'Méthode non autorisée.',
        'error': True
    }, status=405)
    


