from ..models import Invoice
from ..services.currency_converter import convert_currency
from .base import BaseInvoiceSerializer

class InvoiceCreateSerializer(BaseInvoiceSerializer):
    """Serializer for creating invoices"""
    
    def create(self, validated_data):
        account = self.context['account']
        original_currency = validated_data['original_currency']
        original_amount = float(validated_data['original_amount'])
        
        converted_amount, exchange_rate = convert_currency(
            original_amount, 
            original_currency,
            'USD'
        )
        
        return Invoice.objects.create(
            account=account,
            **validated_data,
            converted_amount=converted_amount,
            exchange_rate=exchange_rate,
        )