from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """
    Webhook endpoint for payment provider callbacks.
    Currently returns 501 Not Implemented (stub).
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Handle payment provider webhook.
        """
        # In production, this would:
        # 1. Verify webhook signature
        # 2. Parse payment update
        # 3. Update PaymentTransaction status
        # 4. Update Order status
        # 5. Send confirmation email

        return Response(
            {
                'success': False,
                'message': 'Webhook processing not implemented. Use stub provider for testing.'
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
