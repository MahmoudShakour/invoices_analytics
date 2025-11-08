from rest_framework import serializers
from ..models import Invoice

class BaseInvoiceSerializer(serializers.ModelSerializer):
    """Base invoice validation logic"""
    class Meta:
        model = Invoice
        fields = ['original_amount', 'original_currency', 'status']
    
    def validate_original_currency(self, value):
        if not value or len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code")
        return value.upper()
    
    def validate_original_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_status(self, value):
        if value not in ['PENDING', 'PAID']:
            raise serializers.ValidationError("Status must be either PENDING or PAID")
        return value