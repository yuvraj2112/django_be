from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from buyer.models import Buyer, Order
from buyer.serializers import BuyerSerializer, OrderSerializer
from seller.models import Seller, Store, Product
from seller.serializers import SellerSerializer, StoreSerializer, ProductSerializer
from django.db import connection, DatabaseError, transaction
from django.db.models import F
from collections import OrderedDict 
from operator import getitem
from django.conf import settings
import redis
import uuid
import json

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


'''
  /buyer/login
  POST: Login using mobile number

  @body: {
    mobile: string
  }
  @returns: {
    token: user token
  }
'''
class BuyerLogin(APIView):
  def post(self, request):
    data = JSONParser().parse(request)
    mobileData = { 'mobile': data['mobile'] }
    mobile = data['mobile']
    try:
      user = Buyer.objects.get(mobile=mobile)
      userData = BuyerSerializer(user)
      
      #TODO: JWT instead of a simple token?
      data['token'] = userData.data['slug']
      return JsonResponse(data, status=201)
    except Buyer.DoesNotExist:
      serializer = BuyerSerializer(data=mobileData)
      if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return JsonResponse({'token': data['slug']}, status=200)
    return JsonResponse(status=500)


'''
  /buyer/cart/{key}
  POST: Add product to existing redis_cart or new cart

  @parameter: {
    key: string -- redis key, optional
  }
  @body: {
    id: string -- product id
  }
  @returns: {
    key: redis key,
    cart: cart items
  }
  ```````````````````
  /buyer/cart/key
  DELETE: Remove product from existing redis_cart

  @parameter: {
    key: string -- redis key
  }
  @body: {
    id: string -- product id
  }
  @returns: {
    key: redis key,
    cart: cart items
  }
'''
class BuyerCart(APIView):
  def post(self, request, key=None):
    new_data = JSONParser().parse(request)
    cart = {}
    if key == None:
      # create a redis key and initialize cart
      key = str(uuid.uuid4())
      cart = {}
    else:
      # load cart
      cart = redis_instance.get(key)
      cart = json.loads(cart)

    product_id = new_data['id']
    try:
      product = Product.objects.get(id=product_id)
      product = ProductSerializer(product)
      meta = product.data

      product_id = str(product_id)
      try:
        cart[product_id]['req'] = cart[product_id]['req'] + 1
        cart[product_id]['stock'] = meta['count']
        cart[product_id]['sale_price'] = meta['sale_price']
        cart[product_id]['name'] = meta['name']
      except KeyError:
        cart[product_id] = {
          'req': 1,
          'stock': meta['count'],
          'sale_price': meta['sale_price'],
          'name': meta['name']
        }
      # if order greater than stock
      if cart[product_id]['req'] > cart[product_id]['stock']:
        return HttpResponse(status=412)

      redis_instance.set(key, json.dumps(cart))
      response = dict(zip(['key', 'cart'], [key, cart]))
      return JsonResponse(response, status=200)

    except Product.DoesNotExist:
      return HttpResponse(status=400)

    return HttpResponse(status=500)

  def delete(self, request, key=None):
    del_data = JSONParser().parse(request)
    cart = {}
    if key == None:
      return HttpResponse(status=400)
    else:
      # load cart
      cart = redis_instance.get(key)
      cart = json.loads(cart)

    product_id = del_data['id']
    try:
      product = Product.objects.get(id=product_id)
      product = ProductSerializer(product)
      meta = product.data

      product_id = str(product_id)
      try:
        cart[product_id]['req'] = cart[product_id]['req'] - 1
        cart[product_id]['stock'] = meta['count']
        cart[product_id]['sale_price'] = meta['sale_price']
        cart[product_id]['name'] = meta['name']
      except KeyError:
        # product doesn't exist in the cart anyway 
        response = dict(zip(['key', 'cart'], [key, cart]))
        return JsonResponse(response, status=200)
      # if order greater than stock
      if cart[product_id]['req'] == 0:
        del cart[product_id]

      redis_instance.set(key, json.dumps(cart))
      response = dict(zip(['key', 'cart'], [key, cart]))
      return JsonResponse(response, status=200)

    except Product.DoesNotExist:
      return HttpResponse(status=400)

    return HttpResponse(status=200)


'''
  /buyer/order/token
  POST: Place order to a store

  @parameter: {
    token: string -- user token issued upon login
  }
  @body: {
    link: string -- store link provided by buyer
    cart_id: sting -- redis key
  }
'''
class BuyerOrder(APIView):
  def post(self, request, token):
    data = JSONParser().parse(request)
    link = data['link']
    store_slug = link.split('/')[len(link.split('/')) - 1]
    redis_key = data['cart_id']
    customer_slug = token

    # fetch order by key, store id and customer id
    store = Store.objects.get(slug=store_slug)
    storeData = StoreSerializer(store)
    store_id = storeData.data['id']

    user = Buyer.objects.get(slug=customer_slug)
    userData = BuyerSerializer(user)
    customer_id = userData.data['id']

    cart = redis_instance.get(redis_key)
    cart = json.loads(cart)
    order_create = []
    
    # create order for sellers by products and update product quantities
    with transaction.atomic():
      for item in cart.keys():
        order_create.append(Order(store_id=store_id, customer_id=customer_id, product_id=item, quantity=cart[item]['req']))
        products = Product.objects.filter(id=item).update(count=F('count') - cart[item]['req'])
      Order.objects.bulk_create(order_create)
    return HttpResponse(status=200)


'''
  /buyer/store?link=<link>
  GET: Get store details for a buyer

  @query: {
    link: string -- store link provided by buyer
  }
  @returns: {
    Store details
  }
'''
class BuyerStore(APIView):
  def get(self, request):
    link = request.GET.get('link', None)
    store_slug = link.split('/')[len(link.split('/')) - 1]

    try:
      store = Store.objects.get(slug=store_slug)
      storeData = StoreSerializer(store)
      response = storeData.data
      del response['slug']
      del response['seller_id']
      
      return JsonResponse(response, status=201)
    except Store.DoesNotExist:
      return HttpResponse(status=400)
    return HttpResponse(status=500)


'''
  /buyer/product?link=<link>
  GET: Get product details for a store

  @query: {
    link: string -- store link provided by buyer
  }
  @returns: {
    Product catalog details
  }
'''
class BuyerProducts(APIView):
  def get(self, request):
    link = request.GET.get('link', None)
    seller_slug = link.split('/')[len(link.split('/')) - 3]

    try:
      user = Seller.objects.get(slug=seller_slug)
      userData = SellerSerializer(user)
      userId = int(userData.data['id'])
      
      #TODO: Explore a more efficient approach, if time permits
      with connection.cursor() as cursor:
        cursor.execute("select sp.*, CC.name as categ_name, CC.count from seller_product sp inner join (select sp1.category_id, sc.name, count(category_id) from seller_product sp1 inner join seller_category sc on sp1.category_id = sc.id where sp1.seller_id = 1 group by sp1.category_id, sc.name) as CC on CC.category_id = sp.category_id where sp.seller_id = 1 order by CC.count")
        desc = [
          dict(zip([col[0] for col in cursor.description], row)) 
          for row in cursor.fetchall() 
        ]
        dict_x = {}
        for item in desc:
          value = {'name': item['name'], 'description': item['description'], 'id': item['id']}
          try:
            dict_x[item['categ_name']]['count'] = item['count']
            dict_x[item['categ_name']]['items'].append(value)
            values = dict_x[item['categ_name']]
          except KeyError:
              dict_x[item['categ_name']] = {
                'count': item['count'],
                'items': [value]
              }
        data = OrderedDict(sorted(dict_x.items(), key = lambda x: getitem(x[1], 'count'), reverse=True))
      return JsonResponse(data, status=200, safe=False)
    except Seller.DoesNotExist:
      return HttpResponse(status=400)

    return HttpResponse(status=500)
