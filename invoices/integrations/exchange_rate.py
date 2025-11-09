import requests
from django.conf import settings
import logging
from invoices.utils.redis_client import get_redis_client

logger = logging.getLogger(__name__)

class ExchangeRateAPI:
    def __init__(self):
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_url = settings.EXCHANGE_RATE_BASE_URL
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
                return float(cached_rate)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid cached value for {cache_key}: {e}")
        except Exception as e:
            logger.error(f"Redis error retrieving {cache_key}: {e}")
        
        return None
    
    def _set_cached_rate(self, from_currency: str, to_currency: str, rate: float):
        """Set exchange rate in Redis cache with 5-minute expiry"""
        cache_key = self._get_cache_key(from_currency, to_currency)
        try:
            self.redis_client.setex(cache_key, self.cache_expiry, str(rate))
        except Exception as e:
            logger.error(f"Redis error caching {cache_key}: {e}")
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate from one currency to another with Redis caching
        Returns the exchange rate as float
        """
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            if from_currency == to_currency:
                return 1.0
            
            exchange_rate = self._get_cached_rate(from_currency, to_currency)
            if exchange_rate is not None:
                return exchange_rate
            
            url = f"{self.base_url}/{self.api_key}/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') != 'success':
                raise Exception(f"API error: {data.get('error-type', 'Unknown error')}")
            
            rates = data.get('conversion_rates', {})
            
            if to_currency not in rates:
                raise ValueError(f"Currency {to_currency} not supported by API")
            
            exchange_rate = rates[to_currency]
            
            self._set_cached_rate(from_currency, to_currency, exchange_rate)
            
            logger.info(f"Retrieved and cached exchange rate {from_currency}->{to_currency}: {exchange_rate}")
            
            return float(exchange_rate)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching exchange rate: {e}")
            raise Exception(f"Failed to fetch exchange rate: {e}")
        except ValueError as e:
            logger.error(f"Value error processing exchange rate: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rate: {e}")
            raise

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Convenience function to get exchange rate
    """
    api = ExchangeRateAPI()
    return api.get_exchange_rate(from_currency, to_currency)