# invoices/management/commands/test_redis.py
from django.core.management.base import BaseCommand
from invoices.utils.redis_client import get_redis_client
from invoices.services.currency_converter import CurrencyConverter

class Command(BaseCommand):
    help = 'Test Redis connection and currency conversion'

    def handle(self, *args, **options):
        try:
            # Test Redis connection
            redis_client = get_redis_client()
            redis_client.ping()
            self.stdout.write(
                self.style.SUCCESS('✅ Redis connection successful')
            )
            
            # Test currency conversion
            converter = CurrencyConverter()
            
            # Test conversion (this will cache the result)
            amount = 100
            from_currency = 'USD'
            to_currency = 'EGP'
            
            converted_amount,exchange_rate = converter.convert_currency(amount, from_currency, to_currency)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Currency conversion successful: {amount} {from_currency} = {converted_amount:.2f} {to_currency}, with exchage rate {exchange_rate}')
            )
            
            # Test cache retrieval
            cached_exchange_rate = converter._get_cached_rate(from_currency, to_currency)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cache retrieval successful: exchage rate {cached_exchange_rate}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {e}')
            )