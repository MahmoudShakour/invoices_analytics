from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Invoice
from invoices.integrations.exchange_rate import get_exchange_rate


class InvoiceExchangeRateAPIView(APIView):
    """
    Get exchange rate for a specific invoice
    """
    permission_classes = [IsAuthenticated]
    
    def get_invoice(self, pk, user_account):
        """
        Get invoice and verify it belongs to user's account
        """
        invoice = get_object_or_404(Invoice, pk=pk)
        if invoice.account != user_account:
            return None, "You don't have permission to access this invoice"
        return invoice, None
    
    def get(self, request, pk):
        """
        Get exchange rate information for a specific invoice
        """
        invoice, error = self.get_invoice(pk, request.user.account)
        if error:
            return Response({"error": error}, status=status.HTTP_403_FORBIDDEN)
        
        exchange_rate = get_exchange_rate(invoice.original_currency,"USD")
        
        response_data = {
            'invoice_id': invoice.id,
            'original_currency': str(invoice.original_currency),
            'used_exchange_rate': str(invoice.exchange_rate),
            'current_exchange_rate': str(exchange_rate),
        }
        return Response(response_data)