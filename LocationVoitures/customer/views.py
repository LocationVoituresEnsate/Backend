from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
import json
from bson import ObjectId
import jwt
from django.conf import settings
from db_connection import db
from bson.son import SON
from datetime import datetime


@csrf_exempt
def create_client(request):
    if request.method == 'POST':
        try:
            # Vérification du token JWT
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    user_role = payload.get('role')  # Récupère le rôle de l'utilisateur du payload du JWT
                except jwt.ExpiredSignatureError:
                    return JsonResponse({'message': 'Token expiré.', 'error': True}, status=401)
                except jwt.InvalidTokenError:
                    return JsonResponse({'message': 'Token invalide.', 'error': True}, status=401)
            else:
                return JsonResponse({'message': 'Token manquant.', 'error': True}, status=401)


            # Récupérer les données de la requête
            data = json.loads(request.body)

            required_fields = ["first_name", "last_name", "email"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return JsonResponse({
                    'message': f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}.",
                    'error': True
                }, status=400)

            # Vérifie si un client avec cet email existe déjà
            if Client.find_by_email(data["email"]):
                return JsonResponse({
                    'message': "Un client avec cet email existe déjà.",
                    'error': True
                }, status=400)

            # Création du client
            client = Client(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone_number=data.get("phone_number"),
                address=data.get("address"),
                license_number=data.get("license_number"),
                license_country=data.get("license_country"),
                rented_vehicles=data.get("rented_vehicles", []),
            )
            client.save()

            return JsonResponse({
                'message': 'Client créé avec succès!',
                'client_id': str(client._id),
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone_number': client.phone_number,
                'address': client.address,
                'license_number': client.license_number,
                'license_country': client.license_country,
                'rented_vehicles': client.rented_vehicles,
                'date_joined': client.date_joined.isoformat(),
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)



@csrf_exempt
def get_client(request, client_id):
    try:
        client = Client.collection().find_one({'_id': ObjectId(client_id)})
        if not client:
            return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)

        c = Client(**client)
        return JsonResponse({
            'client_id': str(c._id),
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone_number': c.phone_number,
            'address': c.address,
            'license_number': c.license_number,
            'license_country': c.license_country,
            'rented_vehicles': c.rented_vehicles,
            'date_joined': c.date_joined.isoformat(),
        })

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)


@csrf_exempt
def update_client(request, client_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            client_data = Client.collection().find_one({'_id': ObjectId(client_id)})
            if not client_data:
                return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)

            client = Client(**client_data)

            for field in ['first_name', 'last_name', 'email', 'phone_number', 'address', 'license_number', 'license_country', 'rented_vehicles']:
                if field in data:
                    setattr(client, field, data[field])

            client.save()

            return JsonResponse({
                'message': 'Client mis à jour avec succès!',
                'client_id': str(client._id),
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone_number': client.phone_number,
                'address': client.address,
                'license_number': client.license_number,
                'license_country': client.license_country,
                'rented_vehicles': client.rented_vehicles,
                'date_joined': client.date_joined.isoformat(),
            })

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)


@csrf_exempt
def delete_client(request, client_id):
    if request.method == 'DELETE':
        try:
            result = Client.collection().delete_one({'_id': ObjectId(client_id)})
            if result.deleted_count == 0:
                return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)

            return JsonResponse({'message': 'Client supprimé avec succès!'}, status=204)

        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)


@csrf_exempt
def get_all_clients(request):
    try:
        clients_cursor = Client.collection().find()
        clients_data = []
        for doc in clients_cursor:
            c = Client(**doc)
            clients_data.append({
                'client_id': str(c._id),
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'phone_number': c.phone_number,
                'address': c.address,
                'license_number': c.license_number,
                'license_country': c.license_country,
                'rented_vehicles': c.rented_vehicles,
                'date_joined': c.date_joined.isoformat(),
            })

        return JsonResponse({'clients': clients_data}, safe=False)

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)


@csrf_exempt
def total_clients(request):
    try:
        total = Client.count_clients()
        return JsonResponse({'client_count': total})
    except Exception as e:
        return JsonResponse({'message': f'Erreur : {str(e)}', 'error': True}, status=500)


clients = db['client']  # ou le nom exact de ta collection client

@csrf_exempt
def clients_per_month(request):
    try:
        current_year = datetime.now().year
        months = list(range(1, 13))

        pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': { '$year': '$date_joined' },
                        'month': { '$month': '$date_joined' }
                    },
                    'count': { '$sum': 1 }
                }
            },
            { '$sort': SON([('_id.year', 1), ('_id.month', 1)]) }
        ]

        data = list(clients.aggregate(pipeline))

        grouped = {item['_id']['month']: item['count'] for item in data if item['_id']['year'] == current_year}

        # Assurer qu'on retourne les 12 mois, même si le mois n’existe pas dans les résultats
        formatted = [
            {
                'month': month,
                'count': grouped.get(month, 0)
            }
            for month in months
        ]

        return JsonResponse({'data': formatted})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)