from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password as django_check_password
from .models import Manager  # ta classe Manager
from bson import ObjectId
from datetime import datetime

import logging

# Configuration des logs
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Configure le niveau de log ici (DEBUG, INFO, WARNING, etc.)

@csrf_exempt
def create_manager_view(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)

        # Champs obligatoires
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return JsonResponse({'message': f'Champs manquants : {", ".join(missing)}'}, status=400)

        # Vérifie si l'email existe déjà dans la collection 'Auth'
        if Manager.find_by_email(data['email'], collection_name='Auth'):
            return JsonResponse({'message': 'Email déjà utilisé.'}, status=400)

        # Hachage du mot de passe avec Django's PBKDF2
        hashed_str = make_password(data['password'])  # Utilisation de Django's make_password

        # Crée le manager
        manager = Manager(
            username=data['username'],
            email=data['email'],
            password=hashed_str,  # Mot de passe haché
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number'),
            address=data.get('address')
        )
        # Sauvegarde dans la collection 'Auth' (ou autre si tu veux)
        manager.save(collection_name='Auth')

        return JsonResponse({'message': 'Manager créé avec succès', 'id': str(manager._id)}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'message': 'JSON invalide.'}, status=400)
    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}'}, status=500)



@csrf_exempt
def get_all_managers(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    try:
        managers = Manager.find_all(collection_name='Auth')
        managers = [m for m in managers if m.role == 'manager']

        count = len(managers)
        if count == 0:
            return JsonResponse({'message': 'Manager non trouvé.', 'error': True}, status=404)

        data = []
        for m in managers:
            # Vérifier que date_joined est un datetime avant isoformat
            if isinstance(m.date_joined, datetime):
                date_joined_str = m.date_joined.isoformat()
            else:
                date_joined_str = str(m.date_joined) if m.date_joined else None

            data.append({
                'id': str(m._id),
                'username': m.username,
                'email': m.email,
                'first_name': m.first_name,
                'last_name': m.last_name,
                'phone_number': m.phone_number,
                'password': m.password,  
                'address': m.address,
                'role': m.role,
                'date_joined': date_joined_str,
            })

        return JsonResponse({'managers': data}, status=200)
    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}'}, status=500)


  
  
@csrf_exempt
def delete_manager(request, manager_id):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

    try:
        # Vérifie que l'id est valide
        try:
            obj_id = ObjectId(manager_id)
        except Exception:
            return JsonResponse({'message': 'ID invalide'}, status=400)

        # Supprime le manager dans la collection 'Auth'
        result = Manager.collection('Auth').delete_one({'_id': obj_id})

        if result.deleted_count == 0:
            return JsonResponse({'message': 'Manager non trouvé'}, status=404)

        return JsonResponse({'message': 'Manager supprimé avec succès'}, status=200)

    except Exception as e:
        return JsonResponse({'message': f'Erreur serveur : {str(e)}'}, status=500)    


@csrf_exempt
def update_manager(request, manager_id):
    if request.method != 'PUT':
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'JSON invalide.'}, status=400)

    try:
        email = data.get('email')
        if email:
            existing = Manager.find_by_email_exclude_id(email, exclude_id=manager_id)
            if existing:
                return JsonResponse({'message': 'Email déjà utilisé par un autre manager.'}, status=400)

        if 'password' in data and data['password']:
            # Hachage du mot de passe avec Django's PBKDF2 (via make_password)
            logger.info(f"Changement de mot de passe demandé pour le manager {manager_id}")
            hashed_password = make_password(data['password'])
            data['password'] = hashed_password
            logger.info(f"Mot de passe hashé avec succès pour le manager {manager_id}")
        else:
            # Si aucun mot de passe n'est fourni, le champ 'password' est supprimé
            data.pop('password', None)

        # Met à jour les données du manager
        success = Manager.update_manager(manager_id, data, collection_name='Auth')
        if not success:
            return JsonResponse({'message': 'Manager non trouvé ou rien à mettre à jour.'}, status=404)

        logger.info(f"Manager {manager_id} mis à jour avec succès")
        return JsonResponse({'message': 'Manager mis à jour avec succès.'}, status=200)

    except ValueError as ve:
        logger.error(f"Erreur de validation: {ve}")
        return JsonResponse({'message': str(ve)}, status=400)
    except Exception as e:
        logger.error(f"Erreur serveur: {e}")
        return JsonResponse({'message': f'Erreur serveur : {str(e)}'}, status=500)
  

@csrf_exempt
def get_manager_count(request):
    try:
        # Appel de la méthode count_managers pour obtenir le nombre de managers
        manager_count = Manager.count_managers(collection_name='Auth')
        
        # Retourner le nombre de managers dans une réponse JSON
        return JsonResponse({'manager_count': manager_count}, status=200)
    
    except Exception as e:
        # En cas d'erreur, renvoyer une erreur serveur
        return JsonResponse({'message': f'Erreur serveur : {str(e)}'}, status=500)