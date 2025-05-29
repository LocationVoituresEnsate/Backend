from datetime import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse, redirect
from .models import voitures_collection
from django.views.decorators.csrf import csrf_exempt
from bson.objectid import ObjectId


from django.contrib.auth import get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth import authenticate, login


# Create your views here.
def home(request):
    return render(request,"home.html")
def index(request):
    return HttpResponse("app is running ...")

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def add_voiture(request):
    if request.method == 'POST':
        try:
            # Récupération des champs simples (comme tu as déjà fait)
            brand = request.POST.get('brand', '')
            model = request.POST.get('model', '')
            year = int(request.POST.get('year', 0))
            registrationNumber = request.POST.get('registrationNumber', '')
            color = request.POST.get('color', '')
            dailyPrice = float(request.POST.get('dailyPrice', 0))
            mileage = int(request.POST.get('mileage', 0))
            fuelType = request.POST.get('fuelType', '')
            transmission = request.POST.get('transmission', '')
            engineSize = float(request.POST.get('engineSize', 0))
            power = int(request.POST.get('power', 0))
            doors = int(request.POST.get('doors', 4))
            seats = int(request.POST.get('seats', 5))
            trunkCapacity = int(request.POST.get('trunkCapacity', 0))
            insuranceNumber = request.POST.get('insuranceNumber', '')
            insuranceExpiry = request.POST.get('insuranceExpiry', '')
            technicalInspectionDate = request.POST.get('technicalInspectionDate', '')
            nextInspectionDue = request.POST.get('nextInspectionDue', '')
            condition = request.POST.get('condition', 'Bon')
            comments = request.POST.get('comments', '')

            photos = request.FILES.getlist('photos')  # Liste des fichiers envoyés
            imageUrl = ''

            if photos:
                # Enregistre la première photo dans MEDIA_ROOT / images/
                photo = photos[0]
                path = default_storage.save(f'images/{photo.name}', ContentFile(photo.read()))

                # Génère l’URL complète accessible publiquement
                imageUrl = request.build_absolute_uri(f'/media/{path}')

            voiture_data = {
                "brand": brand,
                "model": model,
                "year": year,
                "registrationNumber": registrationNumber,
                "color": color,
                "dailyPrice": dailyPrice,
                "mileage": mileage,
                "fuelType": fuelType,
                "transmission": transmission,
                "engineSize": engineSize,
                "power": power,
                "doors": doors,
                "seats": seats,
                "trunkCapacity": trunkCapacity,
                "insuranceNumber": insuranceNumber,
                "insuranceExpiry": insuranceExpiry,
                "technicalInspectionDate": technicalInspectionDate,
                "nextInspectionDue": nextInspectionDue,
                "imageUrl": imageUrl,
                "condition": condition,
                "comments": comments,
                "available": True,
                "reservation_periods": [],
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            voitures_collection.insert_one(voiture_data)

            return JsonResponse({"message": "Voiture ajoutée avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


def serialize_voiture(voiture):
    # Convertit un document MongoDB en dict JSON-serializable
    d = dict(voiture)
    d['_id'] = str(d['_id'])
    for field in ['createdAt', 'updatedAt']:
        if field in d and isinstance(d[field], datetime):
            d[field] = d[field].isoformat()
    return d

@csrf_exempt
def get_all_voitures(request):
    voitures_cursor = voitures_collection.find()
    voitures_list = [serialize_voiture(v) for v in voitures_cursor]
    return JsonResponse(voitures_list, safe=False)  

@csrf_exempt
def update_voiture(request, voiture_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            update_data = {
                "brand": data.get('brand'),
                "model": data.get('model'),
                "year": int(data['year']) if 'year' in data else None,
                "registrationNumber": data.get('registrationNumber'),
                "color": data.get('color'),
                "dailyPrice": float(data['dailyPrice']) if 'dailyPrice' in data else None,
                "mileage": int(data['mileage']) if 'mileage' in data else None,
                "fuelType": data.get('fuelType'),
                "transmission": data.get('transmission'),
                "engineSize": float(data['engineSize']) if 'engineSize' in data else None,
                "power": int(data['power']) if 'power' in data else None,
                "doors": int(data['doors']) if 'doors' in data else None,
                "seats": int(data['seats']) if 'seats' in data else None,
                "trunkCapacity": int(data['trunkCapacity']) if 'trunkCapacity' in data else None,
                "insuranceNumber": data.get('insuranceNumber'),
                "insuranceExpiry": data.get('insuranceExpiry'),
                "technicalInspectionDate": data.get('technicalInspectionDate'),
                "nextInspectionDue": data.get('nextInspectionDue'),
                "imageUrl": data.get('imageUrl'),
                "condition": data.get('condition'),
                "comments": data.get('comments'),
                "available": data.get('available'),
                "updatedAt": datetime.datetime.now()
            }

            # Supprimer les clés avec des valeurs None pour éviter de les écraser
            update_data = {k: v for k, v in update_data.items() if v is not None}

            result = voitures_collection.update_one(
                {"_id": ObjectId(voiture_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return JsonResponse({"error": "Voiture non trouvée"}, status=404)

            return JsonResponse({"message": "Voiture mise à jour avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@csrf_exempt
def delete_voiture(request, voiture_id):
    if request.method == 'DELETE':
        try:
            try:
                object_id = ObjectId(voiture_id)
            except:
                return JsonResponse({"error": "ID invalide"}, status=400)

            result = voitures_collection.delete_one({"_id": object_id})

            if result.deleted_count == 0:
                return JsonResponse({"error": "Voiture non trouvée"}, status=404)

            return JsonResponse({"message": "Voiture supprimée avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@csrf_exempt
def count_voitures(request):
    try:
        total = voitures_collection.count_documents({})
        return JsonResponse({'count_voitures': total})
    except Exception as e:
        return JsonResponse({'message': f'Erreur : {str(e)}', 'error': True}, status=500)