from invoices.integrations.exchange_rate import get_exchange_rate
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class CurrencyConverter:
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
        """
        Convert amount from one currency to another
        Returns (converted_amount, exchange_rate)
        """
        try:
            if not isinstance(amount, (int, float)) or amount < 0:
                raise ValueError("Amount must be a positive number")
            
            from_currency = from_currency.upper().strip()
            to_currency = to_currency.upper().strip()
            
            if from_currency == to_currency:
                return float(amount), 1.0
            
            exchange_rate = get_exchange_rate(from_currency, to_currency)
            converted_amount = amount * exchange_rate   
                     
            return converted_amount, exchange_rate
            
        except Exception as e:
            logger.error(f"Currency conversion error: {e}")
            raise

def convert_currency(amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
    """
    Convenience function to convert currency
    """
    converter = CurrencyConverter()
    return converter.convert_currency(amount, from_currency, to_currency)