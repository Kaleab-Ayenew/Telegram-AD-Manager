from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .serializers import TempSellerSerializer, UserCreateSerializer, SellerSerializer, LoginSerializer, ProductSerializer, PaymentInfoSerializer, TempDownloadLink, WithdrawInfoSerializer
from .models import TemporarySellerData
from . import utils
from . import permissions

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import FileResponse

from uuid import uuid4
import json


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_tempseller(request):
    serializer = TempSellerSerializer(data=request.data)
    if serializer.is_valid():
        tempseller_obj = serializer.save()
        utils.send_verification_code(tempseller_obj)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def verify_email(request, temp_data_uuid):
    temp_seller = get_object_or_404(TemporarySellerData, pk=temp_data_uuid)
    code = request.data.get("code")

    if code == temp_seller.verification_code:
        # Create the seller object here
        user_create_data = {"username": temp_seller.seller_email,
                            "password": temp_seller.seller_password, "email": temp_seller.seller_email}
        user_serializer = UserCreateSerializer(data=user_create_data)
        if user_serializer.is_valid():
            new_user = User.objects.create_user(
                **user_serializer.validated_data)
        else:
            return Response(data=user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        seller_create_data = TempSellerSerializer(temp_seller).data
        seller_email = seller_create_data.get("seller_email")
        seller_create_data.update(
            {"main_user": new_user.pk, "seller_username": seller_email})
        seller_serializer = SellerSerializer(data=seller_create_data)

        if seller_serializer.is_valid():
            new_seller = seller_serializer.save()
            return Response(data={"message": "Seller created succesfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(data=seller_serializer.errors)
    else:
        return Response(data={"error": "Wrong Code"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        uname = serializer.validated_data.get("username")
        passwd = serializer.validated_data.get("password")
        user = authenticate(username=uname, password=passwd)
        if user is not None:

            token, _ = Token.objects.get_or_create(user=user)
            rsp_data = {"username": uname, "token": token.key,
                        "uid": uname}
            return Response(data=rsp_data)
        else:
            return Response(data={"error": "Please provide valid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.IsSeller,))
def create_product(request):
    product_serializer = ProductSerializer(data=request.data)

    if product_serializer.is_valid():
        seller_user = utils.get_seller_from_user(request.user)
        new_product = product_serializer.save(product_seller=seller_user)
        return Response(data=product_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(data=product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_payment_link(request, product_id):
    payment_info_serializer = PaymentInfoSerializer(data=request.data)
    if payment_info_serializer.is_valid():
        validated_data = payment_info_serializer.validated_data
        transaction_ref = str(uuid4())
        product_obj = utils.get_product_by_id(product_id)
        payment_link = utils.get_split_payment_link(
            validated_data, product_obj, transaction_ref)
        if payment_link:
            new_sale = utils.create_sale(product_obj, transaction_ref)
            return Response(data={"link": payment_link})

        else:
            return Response(data={"error": "An error has occured"})
    else:
        return Response(data=payment_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((AllowAny,))
def chapa_callback_verify(request, transaction_ref):
    payment_status = utils.verify_payment(transaction_ref)
    if payment_status == "success":
        sale = utils.get_sale_by_tx_ref(transaction_ref)
        sale.completed = True
        sale.save()
        # The Seller total income is updated here
        utils.update_seller_income(sale)
        temp_download_link = utils.create_download_link(sale).link_string()
        rsp_data = {"status": "completed", "download_link": temp_download_link}
        return Response(data=rsp_data)
    elif payment_status == "pending":
        rsp_data = {"status": "pending"}
        return Response(data=rsp_data)
    elif payment_status == "failed":
        sale = utils.get_sale_by_tx_ref(transaction_ref)
        if sale:
            sale.delete()
        rsp_data = {"status": "failed"}
        return Response(data=rsp_data)
    else:
        rsp_data = {"status": "error"}
        return Response(data=rsp_data)


@api_view(['GET'])
@permission_classes((AllowAny,))
def product_download_handler(request, link_id):
    temp_link = utils.get_templink_by_id(link_id)

    if temp_link.is_expired() or temp_link.was_used:
        return Response(data={"error": "Invalid Link"}, status=status.HTTP_404_NOT_FOUND)

    product = utils.get_product_from_link(link_id)
    product_file = product.product_file
    temp_link.was_used = True
    temp_link.save()
    return FileResponse(product_file)


@api_view(['POST'])
@permission_classes((permissions.IsSeller,))
def withdraw_to_bank(request):
    seller = utils.get_seller_from_user(request.user)
    withdraw_info_serializer = WithdrawInfoSerializer(data=request.data)
    current_withdraw_requests = utils.get_withdraw_request(seller)
    if current_withdraw_requests:
        return Response(data={"error": "There is a pending withdrawal request."}, status=status.HTTP_403_FORBIDDEN)
    if withdraw_info_serializer.is_valid():
        if withdraw_info_serializer.validated_data.get("amount") > seller.total_income:
            return Response(data={"error": "Insufficient funds for withdrawal."}, status=status.HTTP_403_FORBIDDEN)
        new_with_request = withdraw_info_serializer.save(seller=seller)
        withdraw_req_response = utils.withdraw_to_bank(new_with_request)
        if withdraw_req_response.get("status") == "success":
            return Response(data={"message": "Withdrawal completed successfully"})
        else:
            return Response(data=withdraw_req_response, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data=withdraw_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_event_webhook(request):
    data = request.data
    chapa_signature = request.headers.get("Chapa-Signature")
    if utils.check_webhook_secret(chapa_signature):
        print(data)
        with_ref = data.get("reference")
        if not with_ref:
            print("Error: Couldn't find withdrawal reference!")
            return Response(status=status.HTTP_200_OK)
        withdraw_request = utils.get_withdrawal_by_reference(with_ref)
        if not withdraw_request:
            print("Error: Couldn't withdrawal by reference!")
            return Response(status=status.HTTP_200_OK)

        withdraw_request.chapa_webhook_data = json.dumps(data)
        withdraw_request.save()
        with_status = data.get("status")
        if with_status == "success":
            utils.withdrawal_deduct(withdraw_request)
            withdraw_request.status = "completed"
            withdraw_request.save()
        elif with_status == "failed":
            withdraw_request.status = "failed"
            withdraw_request.save()
        return Response(status=status.HTTP_200_OK)
    else:
        print(data)
        return Response(status=status.HTTP_200_OK)