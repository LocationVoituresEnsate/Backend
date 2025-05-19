import jwt
from django.http import JsonResponse
from django.conf import settings

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = settings.SECRET_KEY

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        print("Authorization header:", auth_header)  # debug

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                print("JWT payload:", payload)  # debug
                request.user_id = payload.get('user_id')
                request.user_role = payload.get('role', '').lower()
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expiré.', 'error': True}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'message': 'Token invalide.', 'error': True}, status=401)
        else:
            print("Pas d'en-tête Authorization valide.")  # debug
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
        print("User role:", request.user_role)

        if any(request.path.startswith(path) for path in protected_paths):
            allowed_roles = ['manager']
            if request.user_role is None or request.user_role not in allowed_roles:
                return JsonResponse({'message': 'Accès refusé : managers seulement.', 'error': True}, status=403)

        return self.get_response(request)