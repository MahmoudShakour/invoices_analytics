from rest_framework import serializers
from ..models import Invoice
from ..services.currency_converter import convert_currency
from .base import BaseInvoiceSerializer

class InvoiceUpdateSerializer(BaseInvoiceSerializer):
    """Serializer for updating invoices"""
    
    def update(self, instance, validated_data):
        original_currency = validated_data.get('original_currency', instance.original_currency)
        original_amount = float(validated_data.get('original_amount', instance.original_amount))
        
        if (original_currency != instance.original_currency or 
            original_amount != instance.original_amount):
             
            converted_amount, exchange_rate = convert_currency(
                original_amount, 
                original_currency, 
                'USD'
            )
                
            instance.converted_amount = converted_amount
            instance.exchange_rate = exchange_rate
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance