# invoices/integrations/exchange_rate.py
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ExchangeRateAPI:
    def __init__(self):
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_url = settings.EXCHANGE_RATE_BASE_URL
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate from one currency to another
        Returns the exchange rate as float
        """
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            url = f"{self.base_url}/{self.api_key}/latest/{from_currency}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') != 'success':
                logger.error(f"Exchange rate API error: {data.get('error-type', 'Unknown error')}")
                raise Exception(f"API error: {data.get('error-type', 'Unknown error')}")
            
            rates = data.get('conversion_rates', {})
            
            if to_currency not in rates:
                raise ValueError(f"Currency {to_currency} not supported by API")
            
            exchange_rate = rates[to_currency]
            logger.info(f"Retrieved exchange rate {from_currency}->{to_currency}: {exchange_rate}")
            
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