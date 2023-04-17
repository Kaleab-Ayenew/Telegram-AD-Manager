from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import requests

from .utils import request_payment


@api_view(['POST'])
@permission_classes((AllowAny,))
def chapa_pay(request):
    rsp = request_payment(request.data)
    return Response(data=rsp)


@api_view(['POST', 'GET'])
@permission_classes((AllowAny,))
def chapa_callback(request):
    print(request.query_params)
    print(request.data)
    return Response(data={})
