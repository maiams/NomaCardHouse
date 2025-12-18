from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available stock."""
    pass


class CartExpiredError(Exception):
    """Raised when attempting to use an expired cart."""
    pass


class PaymentProviderError(Exception):
    """Raised when payment provider encounters an error."""
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'code': response.status_code,
                'details': response.data if isinstance(response.data, dict) else {}
            }
        }
        response.data = custom_response_data

    return response


def api_response(data=None, message=None, success=True, status_code=status.HTTP_200_OK):
    """
    Standardized API response format.
    """
    response_data = {
        'success': success,
        'data': data,
    }

    if message:
        response_data['message'] = message

    return Response(response_data, status=status_code)
