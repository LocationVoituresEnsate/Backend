import jwt
from django.http import JsonResponse
from django.conf import settings
from utils.token_blacklist import blacklisted_tokens

# puis utilise blacklisted_tokens normalement

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = settings.SECRET_KEY

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            # Vérifie si le token est blacklisté
            if token in blacklisted_tokens:
                return JsonResponse({'message': 'Token révoqué, veuillez vous reconnecter.'}, status=401)

            try:
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                request.user_id = payload.get('user_id')
                request.user_role = payload.get('role', '').lower()
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expiré.', 'error': True}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'message': 'Token invalide.', 'error': True}, status=401)
        else:
            request.user_id = None
            request.user_role = None

        return self.get_response(request)


class ManagerOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_paths = [
            '/voitures/add/',
            '/voitures/get/',
            '/voitures/update/',
            '/voitures/delete/',
        ]

        print("Request path:", request.path)

        # On récupère directement le rôle de l'utilisateur connecté
        user_role = getattr(request, 'user_role', None)


        print("User role:", user_role)

        # Si la requête concerne l'un des chemins protégés, vérifiez le rôle
        if any(request.path.startswith(path) for path in protected_paths):
          allowed_roles = 'manager'
          if user_role is None or user_role not in allowed_roles:
              return JsonResponse(
                  {'message': 'Accès refusé : manager seulement.', 'error': True}, 
                  status=403
              )


            
        # Si tout est OK, passez à la vue suivante
        return self.get_response(request)