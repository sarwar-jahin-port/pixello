from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .aamar_client import aamarPay
import uuid
from rest_framework.decorators import api_view
from django.conf import settings

class InitiatePaymentAPIView(APIView):
    """
    POST { "transactionID": "...", "transactionAmount": "...", "customerName": "...", ... }
    → 302 Redirect to payment URL (or JSON with URL).
    """

    def post(self, request):
        # 1. pull out your payment params from the request body (or set defaults)
        data = request.data
        pay = aamarPay(
            isSandbox=True,
            transactionID=data.get("transactionID", str(uuid.uuid4())),
            transactionAmount=data.get("transactionAmount", "100"),
            customerName=data.get("name", ""),
            customerEmail=data.get("email", ""),
            customerMobile=data.get("phone", ""),
            successUrl=data.get("successUrl", f"{settings.BACKEND_URL}/api/v1/payment/success/"),
            cancelUrl=data.get("cancelUrl", f"{settings.BACKEND_URL}/api/v1/payment/failed/"),
            # … you can pass in other fields too …
        )
        
        # 2. call the client
        payment_url = pay.payment()
        if not payment_url:
            return Response(
                {"detail": "Could not get payment URL"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 3a. Option 1: return JSON with the URL
        return Response({"payment_url": payment_url})

        # 3b. Option 2: redirect the user immediately
        # from django.shortcuts import redirect
        # return redirect(payment_url)

@api_view(['POST', 'GET'])
def payment_success(request):
    # print(request.data.get("transactionID"))
    return redirect(f"{settings.FRONTEND_URL}")

@api_view(['POST', 'GET'])
def payment_failed(request):
    # print(request.data.get("transactionID"))
    return redirect(f"{settings.FRONTEND_URL}")

