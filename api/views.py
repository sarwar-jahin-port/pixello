from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .aamar_client import aamarPay
import uuid
from rest_framework.decorators import api_view
from django.conf import settings
from api.models import Payment
from rest_framework.permissions import IsAuthenticated

class InitiatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. pull out your payment params from the request body (or set defaults)
            data = request.data
            user = request.user
            txid = data.get("transactionID", str(uuid.uuid4()))

            # compute defaults only once:
            default_success = f"{settings.BACKEND_URL}/api/v1/payment/success/"
            default_fail    = f"{settings.BACKEND_URL}/api/v1/payment/failed/"
            default_cancel  = f"{settings.BACKEND_URL}/api/v1/payment/cancelled/"
            
            pay = aamarPay(
                isSandbox=True,
                transactionID      = txid,
                transactionAmount  = data.get("transactionAmount", "100"),
                customerName       = data.get("name", ""),
                customerEmail      = data.get("email", ""),
                customerMobile     = data.get("phone", ""),
                successUrl         = data.get("successUrl", default_success),
                failUrl            = data.get("failUrl", default_fail),
                cancelUrl          = data.get("cancelUrl", default_cancel),
            )
            
            # ✅ Create Payment record only once
            payment = Payment.objects.create(
                user=request.user, 
                transaction_id=pay.transactionID, 
                status='pending'
            )

            # 2. call the client
            payment_url = pay.payment()
            if not payment_url:
                # Clean up the payment record if URL generation fails
                payment.delete()
                return Response(
                    {"detail": "Could not get payment URL"},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # 3a. Option 1: return JSON with the URL
            return Response({"payment_url": payment_url})
            
        except Exception as e:
            return Response(
                {"detail": f"Payment initiation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET','POST'])
def payment_success(request):
    txid = request.GET.get('tran_id') or request.data.get('mer_txnid')
    try:
        payment = Payment.objects.get(transaction_id=txid)
    except Payment.DoesNotExist:
        # Optional: log warning
        return redirect(settings.FRONTEND_URL)

    print(payment)
    # 1️⃣ Mark payment as successful
    payment.status = 'success'
    payment.save(update_fields=['status'])

    # 2️⃣ Upgrade the user
    user = payment.user
    if not user.premium:
        user.premium = True
        user.save()

    # 3️⃣ Redirect to front end
    return redirect(f"{settings.FRONTEND_URL}/dashboard")

@api_view(['GET','POST'])
def payment_failed(request):
    txid = request.GET.get('tran_id') or request.data.get('transactionID')
    try:
        payment = Payment.objects.get(transaction_id=txid)
    except Payment.DoesNotExist:
        return redirect(settings.FRONTEND_URL)

    payment.status = 'failed'
    payment.save(update_fields=['status'])
    return redirect(f"{settings.FRONTEND_URL}/dashboard")

@api_view(['POST', 'GET'])
def payment_cancelled(request):
    return redirect(f"{settings.FRONTEND_URL}")