from rest_framework import permissions

class IsInvoiceAccountOwner(permissions.BasePermission):
    """
    Authorization that only allows access to invoices belonging to user's account
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.account == request.user.account