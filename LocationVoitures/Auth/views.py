import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Auth  # ta classe pymongo personnalisée



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

            user_data = Auth.collection().find_one({'email': email})
            if not user_data:
                return JsonResponse({'message': 'Email ou mot de passe incorrect.', 'error': True}, status=401)

            # Liste des champs attendus par __init__
            allowed_keys = {'_id', 'username', 'email', 'password', 'first_name', 'last_name',
                            'role', 'phone_number', 'address', 'is_staff', 'is_superuser', 'date_joined'}

            filtered_data = {k: v for k, v in user_data.items() if k in allowed_keys}
            user = Auth(**filtered_data)

            if user.check_password(password):
                if user.is_staff or user.is_superuser or user.role in ['admin', 'manager']:
                    return JsonResponse({
                        'message': 'Connexion réussie.',
                        'user_id': str(user._id),
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }, status=200)
                else:
                    return JsonResponse({'message': 'Compte désactivé.', 'error': True}, status=403)
            else:
                return JsonResponse({'message': 'Email ou mot de passe incorrect.', 'error': True}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)
