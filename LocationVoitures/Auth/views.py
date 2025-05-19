import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime, timedelta
import jwt
from .models import Auth  # ta classe pymongo personnalisée
from utils.token_blacklist import blacklisted_tokens

# ajoute le token dans blacklisted_tokens dans ta vue logout


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("[DEBUG] Données reçues :", data)

            email = data.get('email')
            password = data.get('password')
            print(f"[DEBUG] Email: {email}, Password: {'***' if password else None}")

            if not email or not password:
                print("[DEBUG] Champs email ou password manquants")
                return JsonResponse({
                    'message': 'Les champs email et password sont obligatoires.',
                    'error': True
                }, status=400)

            user_data = Auth.collection().find_one({'email': email})
            print("[DEBUG] user_data depuis la base :", user_data)

            if not user_data:
                print("[DEBUG] Aucun utilisateur trouvé avec cet email")
                return JsonResponse({'message': 'Email ou mot de passe incorrect.', 'error': True}, status=401)

            allowed_keys = {
                '_id', 'username', 'email', 'password', 'first_name', 'last_name',
                'role', 'phone_number', 'address', 'is_staff', 'is_superuser', 'date_joined'
            }

            filtered_data = {k: v for k, v in user_data.items() if k in allowed_keys}
            user = Auth(**filtered_data)
            print(f"[DEBUG] Utilisateur créé : {user.username} avec rôle : {user.role}")

            if user.check_password(password):
                print("[DEBUG] Mot de passe correct")
                if user.is_staff or user.is_superuser or user.role in ['admin', 'manager']:
                    print("[DEBUG] Utilisateur autorisé, rôle :", user.role)
                    payload = {
                        'user_id': str(user._id),
                        'email': user.email,
                        'role': user.role,
                        'exp': datetime.utcnow() + timedelta(hours=8)
                    }

                    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                    print("[DEBUG] Token JWT généré")

                    return JsonResponse({
                        'message': 'Connexion réussie.',
                        'user_id': str(user._id),
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'token': token
                    }, status=200)
                else:
                    print("[DEBUG] Compte désactivé ou rôle non autorisé")
                    return JsonResponse({'message': 'Compte désactivé.', 'error': True}, status=403)
            else:
                print("[DEBUG] Mot de passe incorrect")
                return JsonResponse({'message': 'Email ou mot de passe incorrect.', 'error': True}, status=401)

        except json.JSONDecodeError:
            print("[DEBUG] Erreur JSON")
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            print("[DEBUG] Exception :", str(e))
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    print("[DEBUG] Méthode non autorisée")
    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)


# Par exemple, stocke les tokens révoqués en mémoire (à remplacer par une vraie base ou cache Redis)

@csrf_exempt
def logout(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            blacklisted_tokens.add(token)
            return JsonResponse({'message': 'Déconnexion réussie.'}, status=200)
        else:
            return JsonResponse({'message': 'Token manquant.'}, status=400)

    return JsonResponse({'message': 'Méthode non autorisée.'}, status=405)