from django.shortcuts import render,HttpResponse
from .models import person_collection
# Create your views here.
def home(request):
    return render(request,"home.html")
def index(request):
    return HttpResponse("app is running ...")
def add_person(request):
    records = {
        "first_name":"john",
        "last_name":"doe"
    }
    person_collection.insert_one(records)
    return HttpResponse("new person was added")

def get_all_person(request):
    persons=person_collection.find()
    return HttpResponse(persons)