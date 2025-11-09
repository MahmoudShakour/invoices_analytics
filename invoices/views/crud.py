
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from invoices.permissions import IsInvoiceAccountOwner
from ..models import Invoice
from ..serializers import InvoiceSerializer, InvoiceCreateSerializer, InvoiceUpdateSerializer

class InvoiceListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all invoices for the user's account"""
        invoices = Invoice.objects.filter(account_id=request.user.account_id)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new invoice for the user's account"""
        data = request.data.copy()
        serializer = InvoiceCreateSerializer(data=data,context={'account': request.user.account_id})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        invoice = serializer.save()
        
        response_serializer = InvoiceSerializer(invoice)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        

class InvoiceDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInvoiceAccountOwner]
    
    def _get_invoice(self, pk):
        """Get invoice object"""
        invoice = get_object_or_404(Invoice, pk=pk)
        self.check_object_permissions(self.request, invoice)
        return invoice
    
    def get(self, request, pk):
        """Retrieve a specific invoice"""
        invoice = self._get_invoice(pk)
        
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update a specific invoice"""
        invoice = self._get_invoice(pk)
        
        data = request.data.copy()
        
        serializer = InvoiceUpdateSerializer(invoice, data=data)
        if serializer.is_valid():
            updated_invoice = serializer.save()
            response_serializer = InvoiceSerializer(updated_invoice)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete a specific invoice"""
        invoice = self._get_invoice(pk)
        
        invoice.delete()
        
        return Response(
            {"message": "Invoice deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )