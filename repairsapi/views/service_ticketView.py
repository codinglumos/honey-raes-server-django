from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket
from repairsapi.models.customer import Customer
from repairsapi.models.employee import Employee


class serviceTicketView(ViewSet):
    """Honey Rae API ServiceTickets view"""
      
    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests to get all ServiceTickets

        Returns:
            Response -- JSON serialized list of ServiceTickets
        """

        serviceTickets = ServiceTicket.objects.all()
        serialized = ServiceTicketSerializer(serviceTickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single serviceTicket

        Returns:
            Response -- JSON serialized serviceTicket record
        """

        serviceTicket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(serviceTicket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model= Employee
        fields = ('id', 'full_name', 'specialty')

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for serviceTickets"""
    employee = TicketEmployeeSerializer(many=False)

class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Customer
        fields = ('id', 'full_name', 'address')

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for serviceTickets"""
    customer = TicketCustomerSerializer(many=False)
    
    class Meta:
        model = ServiceTicket
        fields = ( 'id', 'description', 'emergency', 'date_completed', 'employee', 'customer' )
        depth = 1