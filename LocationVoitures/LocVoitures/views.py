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

@csrf_exempt
def add_voiture(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            voiture_data = {
                "brand": data.get('brand', ''),
                "model": data.get('model', ''),
                "year": int(data.get('year', 0)),
                "registrationNumber": data.get('registrationNumber', ''),
                "color": data.get('color', ''),
                "dailyPrice": float(data.get('dailyPrice', 0)),
                "mileage": int(data.get('mileage', 0)),
                "fuelType": data.get('fuelType', ''),              
                "transmission": data.get('transmission', ''),      
                "engineSize": float(data.get('engineSize', 0)),    
                "power": int(data.get('power', 0)),               
                "doors": int(data.get('doors', 4)),
                "seats": int(data.get('seats', 5)),
                "trunkCapacity": int(data.get('trunkCapacity', 0)),
                "insuranceNumber": data.get('insuranceNumber', ''),
                "insuranceExpiry": data.get('insuranceExpiry', ''), 
                "technicalInspectionDate": data.get('technicalInspectionDate', ''),
                "nextInspectionDue": data.get('nextInspectionDue', ''),
                "imageUrl": data.get('imageUrl', ''),
                "condition": data.get('condition', 'Bon'),
                "comments": data.get('comments', ''),
                "available": True,
                "reservation_periods": [],  # Champ utilisé pour bloquer les périodes réservées
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            voitures_collection.insert_one(voiture_data)
            return JsonResponse({"message": "Voiture ajoutée avec succès"}, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


def get_all_voitures(request):
    voitures=voitures_collection.find()
    return HttpResponse(voitures)

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


