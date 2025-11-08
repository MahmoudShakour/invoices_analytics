from ..models import Invoice
from rest_framework import serializers

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'id', 'account', 'original_amount', 'original_currency',
            'exchange_rate', 'converted_amount', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'exchange_rate', 'converted_amount', 'created_at']
