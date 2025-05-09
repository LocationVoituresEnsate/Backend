from django.shortcuts import render,HttpResponse, redirect
import json
from django.http import JsonResponse
from .models import user_collection
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login

# Create your views here.

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Champs requis
            required_fields = ["username", "password", "email"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'message': f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}.",
                    'error': True
                }, status=400)

            username = data["username"]
            password = data["password"]
            email = data["email"]

            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            phone_number = data.get("phone_number", "")
            address = data.get("address", "")
            role = data.get("role", "manager")  # Par défaut, manager

            User = get_user_model()

            # Vérifier unicité de l'email et du username
            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Cet email est déjà utilisé.', 'error': True}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'message': 'Ce nom d’utilisateur est déjà utilisé.', 'error': True}, status=400)

            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,  # Haché automatiquement
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                role=role
            )

            # S'assurer que le compte est actif
            user.is_active = True
            user.save()

            return JsonResponse({
                'message': 'Utilisateur créé avec succès!',
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'address': user.address,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)

        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)
  
  


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({
                    'message': 'Les champs email et password sont obligatoires.',
                    'error': True
                }, status=400)

            # Appel à authenticate avec email personnalisé
            user = authenticate(email=email, password=password)

            if user is not None:
                if user.is_active:
                    return JsonResponse({
                        'message': 'Connexion réussie.',
                        'user_id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Compte désactivé.', 'error': True}, status=403)
            else:
                return JsonResponse({
                    'message': 'Email ou mot de passe incorrect.',
                    'error': True
                }, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)



#create manager
@csrf_exempt
def create_manager(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Champs obligatoires pour la création
            required_fields = ["username", "password", "email"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'message': f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}.",
                    'error': True
                }, status=400)

            username = data["username"]
            password = data["password"]
            email = data["email"]

            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            phone_number = data.get("phone_number", "")
            address = data.get("address", "")
            role = 'manager'  # Définir le rôle comme 'manager'

            User = get_user_model()

            # Vérifier unicité de l'email et du username
            if User.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Cet email est déjà utilisé.', 'error': True}, status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'message': 'Ce nom d’utilisateur est déjà utilisé.', 'error': True}, status=400)

            # Créer le manager
            manager = User.objects.create_user(
                username=username,
                email=email,
                password=password,  # Mot de passe haché automatiquement
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                address=address,
                role=role
            )

            manager.is_active = True
            manager.save()

            return JsonResponse({
                'message': 'Manager créé avec succès!',
                'user_id': str(manager.id),
                'username': manager.username,
                'email': manager.email,
                'role': manager.role,
                'first_name': manager.first_name,
                'last_name': manager.last_name,
                'phone_number': manager.phone_number,
                'address': manager.address,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)
  
  
  #get manager by id
  
def get_manager(request, manager_id):
    try:
        manager = get_user_model().objects.get(id=manager_id, role='manager')
        return JsonResponse({
            'user_id': str(manager.id),
            'username': manager.username,
            'email': manager.email,
            'role': manager.role,
            'first_name': manager.first_name,
            'last_name': manager.last_name,
            'phone_number': manager.phone_number,
            'address': manager.address,
        })
    except get_user_model().DoesNotExist:
        return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)



#update manager
@csrf_exempt
def update_manager(request, manager_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            manager = get_user_model().objects.get(id=manager_id, role='manager')

            # Mise à jour des champs
            if 'username' in data:
                manager.username = data['username']
            if 'email' in data:
                manager.email = data['email']
            if 'first_name' in data:
                manager.first_name = data['first_name']
            if 'last_name' in data:
                manager.last_name = data['last_name']
            if 'phone_number' in data:
                manager.phone_number = data['phone_number']
            if 'address' in data:
                manager.address = data['address']

            manager.save()

            return JsonResponse({
                'message': 'Manager mis à jour avec succès!',
                'user_id': str(manager.id),
                'username': manager.username,
                'email': manager.email,
                'role': manager.role,
                'first_name': manager.first_name,
                'last_name': manager.last_name,
                'phone_number': manager.phone_number,
                'address': manager.address,
            })

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except get_user_model().DoesNotExist:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)
  

#delete manager

@csrf_exempt
def delete_manager(request, manager_id):
    if request.method == 'DELETE':
        try:
            manager = get_user_model().objects.get(id=manager_id, role='manager')
            manager.delete()
            return JsonResponse({'message': 'Manager supprimé avec succès!'}, status=204)

        except get_user_model().DoesNotExist:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)


def get_all_managers(request):
    try:
        # Récupérer tous les utilisateurs avec le rôle 'manager'
        managers = get_user_model().objects.filter(role='manager')
        
        # Créer une liste des données des managers à renvoyer
        managers_data = []
        for manager in managers:
            managers_data.append({
                'user_id': str(manager.id),
                'username': manager.username,
                'email': manager.email,
                'role': manager.role,
                'first_name': manager.first_name,
                'last_name': manager.last_name,
                'phone_number': manager.phone_number,
                'address': manager.address,
            })

        # Renvoyer les données des managers
        return JsonResponse({'managers': managers_data}, safe=False)

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)      
      


