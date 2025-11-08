from django.conf import settings
from invoices.integrations.exchange_rate import get_exchange_rate
from invoices.utils.redis_client import get_redis_client
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class CurrencyConverter:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.cache_expiry = getattr(settings, 'CACHE_EXPIRY', 300)
    
    def _get_cache_key(self, from_currency: str, to_currency: str) -> str:
        """Generate Redis cache key for exchange rate"""
        return f"exchange_rate:{from_currency.upper()}:{to_currency.upper()}"
    
    def _get_cached_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate from Redis cache"""
        cache_key = self._get_cache_key(from_currency, to_currency)
        try:
            cached_rate = self.redis_client.get(cache_key)
            if cached_rate:
                rate = float(cached_rate)
                logger.info(f"Cache hit for {from_currency}->{to_currency}: {rate}")
                return rate
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid cached value for {cache_key}: {e}")
        except Exception as e:
            logger.error(f"Redis error retrieving {cache_key}: {e}")
        
        return None
    
    def _set_cached_rate(self, from_currency: str, to_currency: str, rate: float):
        """Set exchange rate in Redis cache"""
        cache_key = self._get_cache_key(from_currency, to_currency)
        try:
            self.redis_client.setex(cache_key, self.cache_expiry, str(rate))
            logger.info(f"Cached exchange rate {from_currency}->{to_currency}: {rate}")
        except Exception as e:
            logger.error(f"Redis error caching {cache_key}: {e}")
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
        """
        Convert amount from one currency to another
        Returns (converted_amount,exchange_rate)
        """
        try:
            if not isinstance(amount, (int, float)) or amount < 0:
                raise ValueError("Amount must be a positive number")
            
            from_currency = from_currency.upper().strip()
            to_currency = to_currency.upper().strip()
            
            if from_currency == to_currency:
                return float(amount), 1.00
            
            exchange_rate = self._get_cached_rate(from_currency, to_currency)
            
            if exchange_rate is None:
                logger.info(f"Cache miss for {from_currency}->{to_currency}, fetching from API")
                exchange_rate = get_exchange_rate(from_currency, to_currency)
                
                self._set_cached_rate(from_currency, to_currency, exchange_rate)
            
            converted_amount = amount * exchange_rate
            logger.info(f"Converted {amount} {from_currency} to {converted_amount:.2f} {to_currency}")
            
            return converted_amount,exchange_rate
            
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            raise

def convert_currency(amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
    """
    Convenience function to convert currency
    """
    converter = CurrencyConverter()
    return converter.convert_currency(amount, from_currency, to_currency)