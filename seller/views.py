from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from seller.models import Seller, Store, Product, Category
from seller.serializers import SellerSerializer, StoreSerializer, ProductSerializer, CategorySerializer
from random import randint


'''
  /seller/login
  POST: Login or sign up using mobile number

  @body: {
    mobile: string
  }
  @returns: {
    token: user token
  }
'''
class SellerLogin(APIView):
  def post(self, request):
    data = JSONParser().parse(request)
    mobileData = { 'mobile': data['mobile'] }
    mobile = data['mobile']
    try:
      user = Seller.objects.get(mobile=mobile)
      userData = SellerSerializer(user)
      data['token'] = userData.data['slug']
      return JsonResponse(data, status=201)
    except Seller.DoesNotExist:
      serializer = SellerSerializer(data=mobileData)
      if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return JsonResponse({'token': data['slug']}, status=200)
    return JsonResponse(status=500)


'''
  /seller/stores/token
  POST: Create new store for the user

  @parameter: {
    token: string -- user token, required
  }
  @body: {
    name: string -- store name
    address: string -- store address
  }
  @returns: {
    id: store's unique ID
    link: store's unique link
  }
  ```````````````````
  /seller/stores/token
  GET: Get all stores registered for the user token

  @parameter: {
    key: string -- user token, required
  }
  @returns: {
    Store details
  }
'''
class SellerStores(APIView):
  def get(self, request, token):
    try:
      user = Seller.objects.get(slug=token)
      userData = SellerSerializer(user)
      userId = userData.data['id']

      stores = Store.objects.filter(seller_id__exact=userId)
      stores = StoreSerializer(stores, many=True)
      return JsonResponse(stores.data, status=200, safe=False)
    except Store.DoesNotExist:
      return Response([], status=200)
    except Seller.DoesNotExist:
      return HttpResponse(status=400)

  def post(self, request, token):
    data = JSONParser().parse(request)
    try:
      user = Seller.objects.get(slug=token)
      userData = SellerSerializer(user)
      userId = userData.data['id']

      data['seller_id'] = userId
      serializer = StoreSerializer(data=data)
      if serializer.is_valid():
        serializer.save()
        data = serializer.data
        returnObj = {
          'id': data['id'],
          'link': f"/{token}/store/{data['slug']}"
        }
        return JsonResponse(returnObj, status=200)
    except Seller.DoesNotExist:
      return HttpResponse(status=400)


'''
  /seller/product/token
  POST: Create new products for the user

  @parameter: {
    token: string -- user token, required
  }
  @multi-part-data, keys: {
    name: string
    description: string
    mrp: string
    sale_price: string
    count: string
    category : string,
    file: Image
  }
  @returns: {
    id: string
    name: string
    image: string -- image url
  }
'''
class SellerProducts(APIView):
  parser_classes = [MultiPartParser]
  def post(self, request, token):
    data = request.data
    try:
      user = Seller.objects.get(slug=token)
      userData = SellerSerializer(user)
      userId = userData.data['id']

      categoryId = None
      try:
        categoryText = data['category']
        categories = Category.objects.get(name__iexact=categoryText)
        categories = CategorySerializer(categories)
        categoryId = categories.data['id']
      except Category.DoesNotExist:
        c_serializer = CategorySerializer(data={'name': data['category']})
        if c_serializer.is_valid():
          c_serializer.save()
          c_data = c_serializer.data
          categoryId = c_data['id']


      prodObj = {
        'name': data['name'],
        'description': data['description'],
        'mrp': data['mrp'],
        'sale_price': data['sale_price'],
        'count': data['count'],
        'image': data['file'],
        'category_id': categoryId,
        'seller_id': userId
      }
      serializer = ProductSerializer(data=prodObj)
      if serializer.is_valid():
        serializer.save()
        product = serializer.data
        returnObj = {
          'id': product['id'],
          'name': data['name'],
          'image': product['image']
        }
        return JsonResponse(returnObj, status=200)
    except Seller.DoesNotExist:
      return HttpResponse(status=400)
