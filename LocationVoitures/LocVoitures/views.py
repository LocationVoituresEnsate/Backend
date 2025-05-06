import datetime
import json
from django.http import JsonResponse
from django.shortcuts import render,HttpResponse
from .models import voitures_collection
from django.views.decorators.csrf import csrf_exempt

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
                "available": True,
                "createdAt": datetime.datetime.now(),
                "updatedAt": datetime.datetime.now()
            }

            voitures_collection.insert_one(voiture_data)
            return JsonResponse({"message": "Voiture ajoutée avec succès"}, status=200)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def get_all_voitures(request):
    voitures=voitures_collection.find()
    return HttpResponse(voitures)