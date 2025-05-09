from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
import json

@csrf_exempt
def create_client(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Champs obligatoires pour la création
            required_fields = ["first_name", "last_name", "email"]
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'message': f"Les champs suivants sont obligatoires : {', '.join(missing_fields)}.",
                    'error': True
                }, status=400)

            # Créer un client
            client = Client.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone_number=data.get("phone_number", ""),
                address=data.get("address", ""),
                license_number=data.get("license_number", ""),
                license_country=data.get("license_country", ""),
                rented_vehicles=data.get("rented_vehicles", []),
            )

            return JsonResponse({
                'message': 'Client créé avec succès!',
                'client_id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone_number': client.phone_number,
                'address': client.address,
                'license_number': client.license_number,
                'license_country': client.license_country,
                'rented_vehicles': client.rented_vehicles,
                'date_joined': client.date_joined,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)


#get client by id

def get_client(request, client_id):
    try:
        client = Client.objects.get(id=client_id)
        return JsonResponse({
            'client_id': client.id,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'phone_number': client.phone_number,
            'address': client.address,
            'license_number': client.license_number,
            'license_country': client.license_country,
            'rented_vehicles': client.rented_vehicles,
            'date_joined': client.date_joined,
        })
    except Client.DoesNotExist:
        return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)


#update client

@csrf_exempt
def update_client(request, client_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            client = Client.objects.get(id=client_id)

            # Mise à jour des champs
            if 'first_name' in data:
                client.first_name = data['first_name']
            if 'last_name' in data:
                client.last_name = data['last_name']
            if 'email' in data:
                client.email = data['email']
            if 'phone_number' in data:
                client.phone_number = data['phone_number']
            if 'address' in data:
                client.address = data['address']
            if 'license_number' in data:
                client.license_number = data['license_number']
            if 'license_country' in data:
                client.license_country = data['license_country']
            if 'rented_vehicles' in data:
                client.rented_vehicles = data['rented_vehicles']

            client.save()

            return JsonResponse({
                'message': 'Client mis à jour avec succès!',
                'client_id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone_number': client.phone_number,
                'address': client.address,
                'license_number': client.license_number,
                'license_country': client.license_country,
                'rented_vehicles': client.rented_vehicles,
                'date_joined': client.date_joined,
            })

        except json.JSONDecodeError:
            return JsonResponse({'message': 'Le format JSON est invalide.', 'error': True}, status=400)
        except Client.DoesNotExist:
            return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)

#delete client

@csrf_exempt
def delete_client(request, client_id):
    if request.method == 'DELETE':
        try:
            client = Client.objects.get(id=client_id)
            client.delete()
            return JsonResponse({'message': 'Client supprimé avec succès!'}, status=204)

        except Client.DoesNotExist:
            return JsonResponse({'message': 'Client non trouvé.', 'error': True}, status=404)
        except Exception as e:
            return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)

    return JsonResponse({'message': 'Méthode non autorisée.', 'error': True}, status=405)

#get all clients

def get_all_clients(request):
    try:
        # Récupérer tous les clients
        clients = Client.objects.all()

        # Créer une liste des clients pour la réponse
        clients_data = []
        for client in clients:
            clients_data.append({
                'client_id': client.id,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'email': client.email,
                'phone_number': client.phone_number,
                'address': client.address,
                'license_number': client.license_number,
                'license_country': client.license_country,
                'rented_vehicles': client.rented_vehicles,
                'date_joined': client.date_joined,
            })

        # Renvoyer la liste des clients
        return JsonResponse({'clients': clients_data}, safe=False)

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}', 'error': True}, status=500)