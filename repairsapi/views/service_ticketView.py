from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket
from repairsapi.models.customer import Customer
from repairsapi.models.employee import Employee


class serviceTicketView(ViewSet):
    """Honey Rae API ServiceTickets view"""
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests to get all ServiceTickets

        Returns:
            Response -- JSON serialized list of ServiceTickets
        """ 
        ticket = ServiceTicket.objects.get(pk=pk)
        ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: NONE with 204 status code
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
        service_tickets = []

        if "status" in request.query_params:
            if request.query_params['status'] == "done":
                service_tickets = ServiceTicket.objects.filter(date_completed__isnull=False)

            if request.query_params['status'] == "all":
                service_tickets = ServiceTicket.objects.all()

        else:
            service_tickets = ServiceTicket.objects.all()


        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single ticket

        Returns:
            Response -- JSON serialized ticket record
        """

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Handle PUT requests for single customer

        Returns: 
            Response -- No response body. Just 204 status code."""

        # Select the targeted ticker using pk
        ticket = ServiceTicket.objects.get(pk=pk)
        # Get the employee id from the client request
        employee_id = request.data['employee']

        # Select the employee from databse using that id
        assigned_employee = Employee.objects.get(pk=employee_id)
        # Assign that Employee instance to the employee property of the ticket
        ticket.employee = assigned_employee
        # Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

class TicketEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model= Employee
        fields = ('id', 'full_name', 'specialty', 'user',)

class TicketCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model= Customer
        fields = ('id', 'full_name', 'address', 'user',)

class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for serviceTickets"""
    customer = TicketCustomerSerializer(many=False)
    employee = TicketEmployeeSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ( 'id', 'description', 'emergency', 'date_completed', 'employee', 'customer',)
        depth = 2