
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Invoice
from ..serializers import InvoiceSerializer, InvoiceCreateSerializer, InvoiceUpdateSerializer

class InvoiceListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all invoices for the user's account"""
        invoices = Invoice.objects.filter(account_id=request.user.account.id)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new invoice for the user's account"""
        data = request.data.copy()
        serializer = InvoiceCreateSerializer(data=data,context={'account': request.user.account})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        invoice = serializer.save()
        
        response_serializer = InvoiceSerializer(invoice)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        

class InvoiceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_invoice(self, pk, user_account):
        """Get invoice and check if it belongs to user's account"""
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.account.id != user_account.id:
            return None, "You don't have permission to access this invoice"
        return invoice, None
    
    def get(self, request, pk):
        """Retrieve a specific invoice"""
        invoice, error = self.get_invoice(pk, request.user.account)
        if error:
            return Response({"error": error}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update a specific invoice"""
        invoice, error = self.get_invoice(pk, request.user.account)
        if error:
            return Response({"error": error}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        
        serializer = InvoiceUpdateSerializer(invoice, data=data)
        if serializer.is_valid():
            updated_invoice = serializer.save()
            response_serializer = InvoiceSerializer(updated_invoice)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete a specific invoice"""
        invoice, error = self.get_invoice(pk, request.user.account)
        if error:
            return Response({"error": error}, status=status.HTTP_403_FORBIDDEN)
        
        invoice.delete()
        
        return Response(
            {"message": "Invoice deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )