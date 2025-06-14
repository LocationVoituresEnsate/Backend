from django.http import JsonResponse
from .models import reservations, clients, voitures
from bson import ObjectId
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from bson.son import SON
from django.views.decorators.http import require_GET
from django.db.models import Sum


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
                    'id': str(voitures['_id']),
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
                # Convertir les IDs en string
                res['_id'] = str(res['_id'])

                # Convertir les IDs en ObjectId si nécessaire
                client_id = ObjectId(res['client_id']) if isinstance(res['client_id'], str) else res['client_id']
                voiture_id = ObjectId(res['voiture_id']) if isinstance(res['voiture_id'], str) else res['voiture_id']

                # Récupérer les données du client
                client = clients.find_one({'_id': client_id})
                res['client'] = {
                    'first_name': client.get('first_name', ''),
                    'last_name': client.get('last_name', ''),
                    'license_number': client.get('license_number', '')
                } if client else {}

                # Récupérer le numéro d'immatriculation de la voiture
                voiture = voitures.find_one({'_id': voiture_id})
                res['registrationNumber'] = voiture.get('registrationNumber', '') if voiture else ''

                # Formater les dates
                res['start_date'] = res['start_date'].strftime('%Y-%m-%d')
                res['end_date'] = res['end_date'].strftime('%Y-%m-%d')
                res['created_at'] = res['created_at'].strftime('%Y-%m-%d %H:%M:%S')

                # Nettoyer les champs techniques
                del res['client_id']
                del res['voiture_id']

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
  
  



@csrf_exempt
def reservations_per_month_status(request):
    try:
        current_year = datetime.now().year
        months = list(range(1, 13))
        statuses = ['pending', 'accepted', 'refused']

        # Pipeline d’agrégation MongoDB
        pipeline = [
            {
                '$group': {
                    '_id': {
                        'year': { '$year': '$created_at' },
                        'month': { '$month': '$created_at' },
                        'status': '$status'
                    },
                    'count': { '$sum': 1 }
                }
            },
            { '$sort': SON([('_id.year', 1), ('_id.month', 1), ('_id.status', 1)]) }
        ]

        data = list(reservations.aggregate(pipeline))

        # Convertir en dict indexé
        grouped = {}
        for item in data:
            y = item['_id']['year']
            m = item['_id']['month']
            s = item['_id']['status']
            grouped.setdefault((y, m), {'year': y, 'month': m, 'pending': 0, 'accepted': 0, 'refused': 0})
            grouped[(y, m)][s] = item['count']

        # Ajouter les mois manquants avec 0
        for month in months:
            key = (current_year, month)
            if key not in grouped:
                grouped[key] = {
                    'year': current_year,
                    'month': month,
                    'pending': 0,
                    'accepted': 0,
                    'refused': 0
                }

        # Trier les résultats par mois
        result = sorted(grouped.values(), key=lambda x: x['month'])

        return JsonResponse({'data': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def total_revenu(request):
    try:
        current_year = datetime.now().year

        pipeline = [
            {
                '$match': {
                    '$expr': { '$eq': [ { '$year': '$start_date' }, current_year ] }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_revenu': { '$sum': '$total_price' }
                }
            }
        ]

        data = list(reservations.aggregate(pipeline))

        total = data[0]['total_revenu'] if data else 0

        # Retourner uniquement le total_revenu
        return JsonResponse({'total_revenu': total})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def count_pending_reservations(request):
    try:
        pending_count = reservations.count_documents({'status': 'pending'})

        return JsonResponse({'pending_reservations_count': pending_count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_GET
def reservations_count_by_voiture(request):
    try:
        # Agrégation pour compter les réservations par voiture
        pipeline = [
            {
                '$group': {
                    '_id': '$voiture_id',
                    'count': { '$sum': 1 }
                }
            }
        ]

        results = list(reservations.aggregate(pipeline))

        # Ajout des infos sur la voiture (par exemple numéro d'immatriculation)
        response = []
        for item in results:
            voiture = voitures.find_one({'_id': item['_id']})
            response.append({
                'voiture_id': str(item['_id']),
                'count': item['count'],
                'registrationNumber': voiture.get('registrationNumber', '') if voiture else ''
            })

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
@require_GET
def top_reserved_vehicles(request):
    try:
        # Pipeline d’agrégation pour compter les réservations par voiture
        pipeline = [
            {
                '$group': {
                    '_id': '$voiture_id',
                    'total_reservations': {'$sum': 1}
                }
            },
            { '$sort': { 'total_reservations': -1 } },
            { '$limit': 5 }  # top 5
        ]

        data = list(reservations.aggregate(pipeline))

        # Enrichir les données avec les infos voiture
        results = []
        for item in data:
            voiture = voitures.find_one({'_id': item['_id']})
            if voiture:
                results.append({
                    'id': str(voiture['_id']),
                    'name': f"{voiture.get('brand', '')} {voiture.get('model', '')}",
                    'bookings': item['total_reservations'],
                    'change': "+0%"  # Valeur par défaut ou à calculer si tu veux
                })

        return JsonResponse({'vehicles': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.http import JsonResponse
from .models import reservations, clients, voitures
from bson import ObjectId
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import json

@csrf_exempt
@require_GET
def recent_reservations(request):
    try:
        # Fetch last 5 reservations, sorted by _id (latest first)
        recent_reservations = list(reservations.find().sort('_id', -1).limit(5))
        results = []
        for res in recent_reservations:
            # Convert IDs if they are strings
            client_id = ObjectId(res['client_id']) if isinstance(res['client_id'], str) else res['client_id']
            voiture_id = ObjectId(res['voiture_id']) if isinstance(res['voiture_id'], str) else res['voiture_id']

            # Get client and car info
            client = clients.find_one({'_id': client_id})
            voiture = voitures.find_one({'_id': voiture_id})

            # Make sure dates are parsed as datetime objects
            start_date = res.get('start_date')
            end_date = res.get('end_date')

            # Format dates
            formatted_start_date = start_date.strftime('%d/%m/%Y') if isinstance(start_date, datetime) else start_date
            formatted_end_date = end_date.strftime('%d/%m/%Y') if isinstance(end_date, datetime) else end_date

            # Calculate total price safely
            if isinstance(start_date, datetime) and isinstance(end_date, datetime):
                days = (end_date - start_date).days + 1  # Include both start and end date
            else:
                days = 0

            daily_price = res.get('daily_price', 0)
            total_price = round(daily_price * days, 2)

            results.append({
                'id': str(res['_id']),
                'client_name': f"{client.get('first_name', '')} {client.get('last_name', '')}" if client else "Inconnu",
                'car_name': f"{voiture.get('brand', '')} {voiture.get('model', '')}" if voiture else "Inconnue",
                'start_date': formatted_start_date,
                'end_date': formatted_end_date,
                'total_price': total_price,
                'status': res.get('status', 'inconnu')
            })

        return JsonResponse({'recent_reservations': results}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
      
@csrf_exempt
@require_GET
def revenu_mensuel(request):
    try:
        current_year = datetime.now().year

        pipeline = [
            {
                # Filtrer sur l'année en cours ET sur les réservations ACCEPTÉES
                '$match': {
                    '$expr': {
                        '$and': [
                            {'$eq': [{'$year': '$start_date'}, current_year]},
                            {'$eq': ['$status', 'accepted']}
                        ]
                    }
                }
            },
            {
                # Grouper par mois de la date de début
                '$group': {
                    '_id': { 'month': { '$month': '$start_date' } },
                    'monthly_revenue': { '$sum': '$total_price' }
                }
            },
            {
                # Trier par mois croissant
                '$sort': SON([('_id.month', 1)])
            }
        ]

        data = list(reservations.aggregate(pipeline))

        # Créer une liste pour tous les mois avec 0 par défaut
        revenue_per_month = {m: 0 for m in range(1, 13)}

        # Remplir avec les données récupérées
        for item in data:
            month = item['_id']['month']
            revenue_per_month[month] = item['monthly_revenue']

        # Préparer la réponse sous forme de liste ordonnée par mois
        result = [{'month': month, 'revenue': revenue_per_month[month]} for month in range(1, 13)]

        return JsonResponse({'revenu_mensuel': result})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
      
      
@csrf_exempt
@require_GET
def reservations_count_per_day(request):
    try:
        current_year = datetime.now().year

        pipeline = [
            {
                # Filtrer uniquement les réservations de l'année en cours (optionnel, à adapter)
                '$match': {
                    '$expr': {
                        '$eq': [{'$year': '$start_date'}, current_year]
                    }
                }
            },
            {
                # Grouper par année, mois, jour pour avoir une date unique par jour
                '$group': {
                    '_id': {
                        'year': { '$year': '$start_date' },
                        'month': { '$month': '$start_date' },
                        'day': { '$dayOfMonth': '$start_date' }
                    },
                    'count': { '$sum': 1 }
                }
            },
            {
                # Trier par date croissante
                '$sort': SON([
                    ('_id.year', 1),
                    ('_id.month', 1),
                    ('_id.day', 1)
                ])
            }
        ]

        data = list(reservations.aggregate(pipeline))

        # Formatage de la réponse pour avoir une date lisible et le nombre
        results = []
        for item in data:
            y = item['_id']['year']
            m = item['_id']['month']
            d = item['_id']['day']
            date_str = f"{y:04d}-{m:02d}-{d:02d}"
            results.append({
                'date': date_str,
                'count': item['count']
            })

        return JsonResponse({'reservations_per_day': results})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)