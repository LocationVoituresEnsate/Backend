from django.http import JsonResponse
from .models import reservations, clients, voitures
from bson import ObjectId
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
def create_reservation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            required_fields = ['client_id', 'voiture_id', 'start_date', 'end_date']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            client_id = ObjectId(data['client_id'])
            voiture_id = ObjectId(data['voiture_id'])

            if not clients.find_one({'_id': client_id}):
                return JsonResponse({'error': 'Client not found'}, status=404)

            voiture = voitures.find_one({'_id': voiture_id})
            if not voiture:
                return JsonResponse({'error': 'Voiture not found'}, status=404)

            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')

            if end_date <= start_date:
                return JsonResponse({'error': 'End date must be after start date'}, status=400)

            days = (end_date - start_date).days
            total_price = voiture['dailyPrice'] * days

            reservation = {
                'client_id': client_id,
                'voiture_id': voiture_id,
                'start_date': start_date,
                'end_date': end_date,
                'daily_price': voiture['dailyPrice'],
                'total_price': total_price,
                'status': 'pending',
                'created_at': datetime.now()
            }

            result = reservations.insert_one(reservation)

            return JsonResponse({
                'id': str(result.inserted_id),
                'client_id': data['client_id'],
                'voiture_id': data['voiture_id'],
                'total_price': total_price,
                'status': 'pending'
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def get_reservation(request, reservation_id):
    if request.method == 'GET':
        try:
            reservation = reservations.find_one({'_id': ObjectId(reservation_id)})
            if not reservation:
                return JsonResponse({'error': 'Reservation not found'}, status=404)

            # Récupération des données liées
            client = clients.find_one({'_id': reservation['client_id']})
            voiture = voitures.find_one({'_id': reservation['voiture_id']})

            response = {
                'id': str(reservation['_id']),
                'client': {
                    'id': str(client['_id']),
                    'name': f"{client.get('firstName', '')} {client.get('lastName', '')}"
                },
                'voiture': {
                    'id': str(voiture['_id']),
                    'brand': voiture.get('brand', ''),
                    'model': voiture.get('model', ''),
                    'daily_price': voiture.get('dailyPrice', 0)
                },
                'start_date': reservation['start_date'].strftime('%Y-%m-%d'),
                'end_date': reservation['end_date'].strftime('%Y-%m-%d'),
                'total_price': reservation.get('total_price', 0),
                'status': reservation.get('status', 'pending')
            }
            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_all_reservations(request):
    if request.method == 'GET':
        try:
            all_reservations = []
            for res in reservations.find():
                res['_id'] = str(res['_id'])
                res['client_id'] = str(res['client_id'])
                res['voiture_id'] = str(res['voiture_id'])
                res['start_date'] = res['start_date'].strftime('%Y-%m-%d')
                res['end_date'] = res['end_date'].strftime('%Y-%m-%d')
                res['created_at'] = res['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                all_reservations.append(res)
            
            return JsonResponse({'reservations': all_reservations}, safe=False)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def accept_reservation(request, reservation_id):
    if request.method == 'POST':
        try:
            reservation = reservations.find_one({'_id': ObjectId(reservation_id)})
            if not reservation:
                return JsonResponse({'error': 'Reservation not found'}, status=404)

            if reservation['status'] != 'pending':
                return JsonResponse({'error': 'Reservation is already processed'}, status=400)

            voiture = voitures.find_one({'_id': reservation['voiture_id']})
            if not voiture:
                return JsonResponse({'error': 'Associated car not found'}, status=404)

            start_date = reservation['start_date']
            end_date = reservation['end_date']

            # ❌ Vérifier si une autre réservation ACCEPTED existe dans cette période
            conflict = reservations.find_one({
                'voiture_id': reservation['voiture_id'],
                'status': 'accepted',
                '_id': {'$ne': reservation['_id']},  # exclure la réservation en cours
                '$or': [
                    {'start_date': {'$lte': end_date}, 'end_date': {'$gte': start_date}}
                ]
            })

            if conflict:
                return JsonResponse({'error': 'Voiture déjà réservée dans cette période'}, status=409)

            # Mise à jour du statut + ajout de la période
            voitures.update_one(
                {'_id': voiture['_id']},
                {
                    '$push': {
                        'reservation_periods': {
                            'start': start_date.strftime('%Y-%m-%d'),
                            'end': end_date.strftime('%Y-%m-%d')
                        }
                    },
                    '$set': {'updatedAt': datetime.now()}
                }
            )

            reservations.update_one(
                {'_id': reservation['_id']},
                {'$set': {'status': 'accepted'}}
            )

            return JsonResponse({'message': 'Réservation acceptée avec succès'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def decline_reservation(request, reservation_id):
    if request.method == 'POST':
        try:
            reservation = reservations.find_one({'_id': ObjectId(reservation_id)})
            if not reservation:
                return JsonResponse({'error': 'Réservation non trouvée'}, status=404)

            if reservation['status'] != 'pending':
                return JsonResponse({'error': 'La réservation est déjà traitée'}, status=400)

            # Récupérer les dates pour libérer la période
            start_str = reservation['start_date'].strftime('%Y-%m-%d')
            end_str = reservation['end_date'].strftime('%Y-%m-%d')

            # Supprimer la période de réservation de la voiture
            voitures.update_one(
                {'_id': reservation['voiture_id']},
                {'$pull': {
                    'reservation_periods': {
                        'start': start_str,
                        'end': end_str
                    }
                }}
            )

            # Mettre à jour le statut
            reservations.update_one(
                {'_id': ObjectId(reservation_id)},
                {'$set': {'status': 'declined'}}
            )

            return JsonResponse({'message': 'Réservation refusée et disponibilité rétablie'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
