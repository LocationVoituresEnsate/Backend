from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User
import json
import traceback


@csrf_exempt
def create_manager(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Données reçues:", data)

            required_fields = ['username', 'email', 'password', 'role']
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return JsonResponse(
                    {'message': f'Champs manquants : {", ".join(missing)}', 'error': True},
                    status=400
                )

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'message': 'Email déjà utilisé.', 'error': True}, status=400)
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({'message': 'Username déjà utilisé.', 'error': True}, status=400)

            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=data['role'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone_number=data.get('phone_number', None),
                address=data.get('address', None)
            )
            
            print(f"User created with ID: {user.id} (type: {type(user.id)})")

            return JsonResponse({'message': 'Manager créé avec succès.', 'user_id': user.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Format JSON invalide.', 'error': True}, status=400)
        except Exception as e:
            print(f"Erreur serveur: {e}")
            traceback.print_exc()
            return JsonResponse({'message': f'Erreur serveur: {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
  
  

@csrf_exempt
def get_manager(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'address': user.address,
            'date_joined': user.date_joined.isoformat(),
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)


@csrf_exempt
def update_manager(request, user_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)

            for field in ['username', 'email', 'role', 'first_name', 'last_name', 'phone_number', 'address']:
                if field in data:
                    setattr(user, field, data[field])

            if 'password' in data:
                user.password = make_password(data['password'])

            # Mettre à jour is_staff et is_superuser selon role
            if 'role' in data:
                user.is_staff = (data['role'] == 'admin')
                user.is_superuser = (data['role'] == 'admin')

            user.save()

            return JsonResponse({'message': 'Manager mis à jour avec succès.'})

        except User.DoesNotExist:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def delete_manager(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': 'Manager supprimé avec succès.'}, status=204)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def get_all_managers(request):
    try:
        managers = User.objects.filter(role='manager')
        count = managers.count()
        print(f"[DEBUG] Nombre de managers trouvés : {count}")
        
        data = []
        for manager in managers:
            data.append({
                'id': manager.id,
                'username': manager.username,
                'email': manager.email,
                'role': manager.role,
                'first_name': manager.first_name,
                'last_name': manager.last_name,
                'phone_number': manager.phone_number,
                'address': manager.address,
                'date_joined': manager.date_joined.isoformat(),
            })
        
        if count == 0:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)

        return JsonResponse({'managers': data})

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur: {str(e)}', 'error': True}, status=500)
