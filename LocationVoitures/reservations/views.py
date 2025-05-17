from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from datetime import datetime
from .models import Voiture, Client, Reservation

def validate_ids(client_id, voiture_id):
    """Validate that both IDs exist in their respective collections"""
    try:
        if not Client.collection.find_one({'_id': ObjectId(client_id)}):
            return False, 'Client not found'
        if not Voiture.collection.find_one({'_id': ObjectId(voiture_id)}):
            return False, 'Voiture not found'
        return True, ''
    except:
        return False, 'Invalid ID format'

@api_view(['POST'])
def create_reservation(request):
    try:
        data = request.data
        
        # Required fields check
        required = ['client_id', 'voiture_id', 'start_date', 'end_date']
        if not all(field in data for field in required):
            return Response(
                {'error': f'Missing required fields: {", ".join(required)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate IDs exist
        valid, message = validate_ids(data['client_id'], data['voiture_id'])
        if not valid:
            return Response(
                {'error': message},
                status=status.HTTP_404_NOT_FOUND
            )

        # Date validation
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        if start_date >= end_date:
            return Response(
                {'error': 'End date must be after start date'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create reservation
        reservation = {
            'client_id': ObjectId(data['client_id']),
            'voiture_id': ObjectId(data['voiture_id']),
            'start_date': start_date,
            'end_date': end_date,
            'created_at': datetime.now(),
            'status': 'active'
        }

        result = Reservation.collection.insert_one(reservation)
        return Response(
            {'id': str(result.inserted_id)},
            status=status.HTTP_201_CREATED
        )

    except ValueError as e:
        return Response(
            {'error': 'Invalid date format. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_reservation(request, reservation_id):
    try:
        reservation = Reservation.collection.find_one({'_id': ObjectId(reservation_id)})
        if not reservation:
            return Response(
                {'error': 'Reservation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get related client and voiture details
        client = Client.collection.find_one({'_id': reservation['client_id']})
        voiture = Voiture.collection.find_one({'_id': reservation['voiture_id']})

        response = {
            'id': str(reservation['_id']),
            'client': {
                'id': str(client['_id']),
                'name': f"{client.get('firstName', '')} {client.get('lastName', '')}"
            },
            'voiture': {
                'id': str(voiture['_id']),
                'name': f"{voiture.get('brand', '')} {voiture.get('model', '')}"
            },
            'start_date': reservation['start_date'].strftime('%Y-%m-%d'),
            'end_date': reservation['end_date'].strftime('%Y-%m-%d'),
            'status': reservation.get('status', 'active')
        }

        return Response(response)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PUT'])
def update_reservation(request, reservation_id):
    try:
        data = request.data
        updates = {}

        # Validate reservation exists
        reservation = Reservation.collection.find_one({'_id': ObjectId(reservation_id)})
        if not reservation:
            return Response(
                {'error': 'Reservation not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validate client_id if provided
        if 'client_id' in data:
            if not Client.collection.find_one({'_id': ObjectId(data['client_id'])}):
                return Response(
                    {'error': 'Client not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            updates['client_id'] = ObjectId(data['client_id'])

        # Validate voiture_id if provided
        if 'voiture_id' in data:
            if not Voiture.collection.find_one({'_id': ObjectId(data['voiture_id'])}):
                return Response(
                    {'error': 'Voiture not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            updates['voiture_id'] = ObjectId(data['voiture_id'])

        # Date updates
        if 'start_date' in data:
            updates['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d')
        if 'end_date' in data:
            updates['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d')

        if updates:
            updates['updated_at'] = datetime.now()
            Reservation.collection.update_one(
                {'_id': ObjectId(reservation_id)},
                {'$set': updates}
            )

        return Response({'message': 'Reservation updated'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
def delete_reservation(request, reservation_id):
    try:
        result = Reservation.collection.delete_one({'_id': ObjectId(reservation_id)})
        if result.deleted_count == 0:
            return Response(
                {'error': 'Reservation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({'message': 'Reservation deleted'})

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )