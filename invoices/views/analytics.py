from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from ..models import Invoice
from ..services.currency_converter import convert_currency

class InvoiceRevenueSummaryAPIView(APIView):
    """
    Get total revenue summary for invoices with exchange rate options.
    Returned total revenue always in USD.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get total revenue summary
        Query parameters:
        - rate: 'historic' (default) or 'current'
        """
        try:
            rate_type = request.GET.get('rate', 'historic').lower()
            
            if rate_type not in ['historic', 'current']:
                return Response(
                    {"error": "rate must be either 'historic' or 'current'"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            success, data, error = self._get_revenue(request.user.account, rate_type)
            
            if not success:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
        
    def _get_revenue(self, account, rate_type):
        """
        Calculate revenue using historic exchange rates from database or currency exchange rates. 
        """
        
        try:
            
            total_revenue = 0
            
            #  if rate_type is historic, sum converted amount and the rate is already applied
            if rate_type == 'historic':
                total_revenue = Invoice.objects.filter(account=account).aggregate(
                    total_revenue=Sum('converted_amount')
                )['total_revenue'] or 0

            # if the rate_type is current, group by the original_currency, sum(original_amount) and compute it programatically.
            else:
                currency_groups = Invoice.objects.filter(account=account).values(
                    'original_currency'
                ).annotate(total_original_amount=Sum('original_amount'))
                
                for group in currency_groups:
                    currency = group['original_currency']
                    amount = group['total_original_amount']
                    
                    converted_amount, _ = convert_currency(float(amount), currency, 'USD')    
                    total_revenue += converted_amount

            return True, {
                'total_revenue': str(total_revenue),
                'currency': 'USD',
                'rate_type': rate_type
            }, None
                
        except Exception as e:
            return False, None, f"Currency conversion failed: {str(e)}"
        

class InvoiceRevenueAverageSizeAPIView(APIView):
    def get(self, request):
        """
        Get average invoice size.
        Fees is applied only if the invoice currency and target currency are different.
        Only Current exchange rates are applied. 
        
        Query parameters:
        - currency: target currency (default: USD)
        """
        target_currency = request.GET.get('currency', 'USD').upper()
        
        if len(target_currency) != 3:
            return Response(
                {"error": "Currency must be a 3-letter code"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, data, error = self._calculate_average_invoice_size(
            request.user.account, 
            target_currency
        )
        
        if not success:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data, status=status.HTTP_200_OK)

        
    def _calculate_average_invoice_size(self,account, target_currency):
        """
        Calculate average invoice size of specified account in the specified currency.
        """
        try:
            currency_stats = Invoice.objects.filter(account=account).values(
                'original_currency'
            ).annotate(
                total_amount=Sum('original_amount'),
                invoice_count=Count('id')
            )
            
            if not currency_stats:
                return True, {
                    'average_amount': '0.00',
                    'currency': target_currency,
                    'invoice_count': 0
                }, None
            
            total_revenue = 0
            total_fees = 0
            number_of_invoices = 0
            
            conversion_fee_percent = getattr(settings, 'CONVERSION_FEE_PERCENT', 2)
            
            for group in currency_stats:
                currency = group['original_currency']
                amount = group['total_amount']
                count = group['invoice_count']
                
                converted_amount, _ = convert_currency(
                    float(amount), currency, target_currency
                )
                
                total_revenue += converted_amount
                number_of_invoices += count
                
                if currency != target_currency:
                    total_fees += ( converted_amount * conversion_fee_percent ) / 100
            
            average_amount = total_revenue / number_of_invoices
            average_amount_after_fees = ( total_revenue - total_fees ) / number_of_invoices
            
            
            return True, {
                'average_size_before_fees': str(round(average_amount, 2)),
                'average_size_after_fees': str(round(average_amount_after_fees, 2)),
                'gross_revenue': str(round(total_revenue, 2)),
                'net_revenue': str(round(total_revenue-total_fees, 2)),
                'currency': target_currency,
                'invoice_count': number_of_invoices,
            }, None
            
        except Exception as e:
            return False, None, f"Average calculation failed: {str(e)}"