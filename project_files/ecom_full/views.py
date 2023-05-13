from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import authenticate


# Create your views here.
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token


from .serializers import ProductSerializer, ProductImageSerializer, OrderSerializer, LoginSerializer
from .permissions import IsAuthAndOwnsObject

from .models import Product, ProductImage, Order
from . import utils
from .permissions import IsEcomAdmin

import datetime


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = []


class ProductRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    permission_classes = [IsEcomAdmin]
    queryset = Product.objects.all()

    def update(self, request, *args, **kwargs):
        rsp = super().update(request, *args, **kwargs)
        product = Product.objects.get(slug=rsp.data.get('slug'))
        img_1 = request.FILES.get("image_1")
        img_2 = request.FILES.get("image_2")
        if img_1:
            image_1 = product.images.all()[0]
            ext = str(image_1.img).split(".")[-1]
            image_1.img.save(f'image.{ext}', img_1)
            image_1.save()
        if img_2:
            image_2 = product.images.all()[1]
            ext = str(image_2.img).split(".")[-1]
            image_2.img.save(f'image.{ext}', img_2)
            image_2.save()

        new_product = Product.objects.get(
            slug=rsp.data.get('slug'))
        serializer = ProductSerializer(new_product)
        # utils.post_to_facebook(new_product)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsEcomAdmin]

    def create(self, request, *args, **kwargs):
        rsp = super().create(request, *args, **kwargs)
        new_product = Product.objects.get(slug=rsp.data.get('slug'))
        img_1 = request.FILES.get("image_1")
        img_2 = request.FILES.get("image_2")
        if img_1:
            image_1 = ProductImage.objects.create(
                product=new_product, img=request.FILES.get('image_1'))
        if img_2:
            image_2 = ProductImage.objects.create(
                product=new_product, img=request.FILES.get('image_2'))

        new_product = new_product = Product.objects.get(
            slug=rsp.data.get('slug'))
        serializer = ProductSerializer(new_product)
        print(request.data, request.data.get('post_to_facebook'))
        if request.data.get('post_to_facebook') == 'on':
            utils.post_to_facebook(new_product)
        if request.data.get('post_to_telegram') == 'on':
            utils.post_to_telegram(new_product)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ImageCreateView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsEcomAdmin]

    def create(self, request, *args, **kwargs):
        serializer = ProductImageSerializer(data=request.data)
        file_list = request.FILES.getlist("img")
        file_data = []
        if serializer.is_valid():
            print(serializer.validated_data.get('product'))
            product_instance = serializer.validated_data.get('product')
            for f in file_list:
                instance = ProductImage.objects.create(
                    product=product_instance, img=f)
                file_data.append(str(instance.img))
            rsp_data = {'product': serializer.data.get(
                'product'), 'img': file_data}
            return Response(data=rsp_data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     rsp_data = []
    #     slug = kwargs['slug']
    #     target_product = get_object_or_404(Product, slug=slug)
    #     print(request.FILES.getlist("file"), request.FILES.getlist("image"))
    #     for f in request.FILES.getlist('file'):
    #         instance = ProductImage.objects.create(parent_product=target_product, image=f)
    #         data = {'parent_product'}
    #         rsp_data.append(data)
    #     return super().create(request, *args, **kwargs)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsEcomAdmin]
    queryset = Order.objects.all()


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = []


@api_view(['GET'])
@permission_classes((IsEcomAdmin,))
def get_sales_data(request):
    past_hr = timezone.now() - datetime.timedelta(hours=2)
    this_hr_orders = Order.objects.filter(order_time__gte=past_hr)
    all_orders = len(Order.objects.all())
    total_sales = this_hr_orders.aggregate(Sum('total_price'))[
        'total_price__sum']
    total_orders = len(this_hr_orders)
    rsp_data = {'total_sales': total_sales,
                'total_orders': total_orders, 'all_orders': all_orders}
    # for order in this_hr_orders:
    #     json_data = OrderSerializer(order).data
    #     json_data.update({'minute': order.order_time.minute})
    #     rsp_data.append(json_data)

    return Response(data=rsp_data)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        uname = serializer.validated_data.get("username")
        passwd = serializer.validated_data.get("password")
        user = authenticate(username=uname, password=passwd)
        if user is not None:
            print(user.username, user.password)
            token, _ = Token.objects.get_or_create(user=user)
            rsp_data = {"username": uname, "token": token.key,
                        "uid": uname, "role": "admin"}
            return Response(data=rsp_data)
        else:
            return Response(data={"error": "Please provide valid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes((IsEcomAdmin))
# def fb_link_view(request):
