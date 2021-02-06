from django.db import models
import uuid
from random import randint

class Seller(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default='')
    mobile = models.CharField(max_length=10, blank=False)
    slug = models.SlugField(max_length=36, default=uuid.uuid4, editable=False)

class Login(models.Model):
    mobile = models.CharField(max_length=10, blank=False)
    otp = models.CharField(max_length=4, blank=False)

class Store(models.Model):
    name = models.CharField(max_length=100, blank=False)
    address = models.TextField(blank=False)
    seller = models.ForeignKey(Seller, default=None, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=36, default=uuid.uuid4, editable=False)

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, default='', blank=False)

class Product(models.Model):
    name = models.CharField(max_length=200, blank=False)
    description = models.TextField(default='', blank=True)
    mrp = models.IntegerField(blank=False, default=0)
    sale_price = models.IntegerField(blank=False, default=0)
    count = models.IntegerField(blank=False, default=0)
    image = models.ImageField(upload_to=f'photos/{randint(0,1000)}/%s')
    category = models.ForeignKey(Category, default=None, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, default=None, on_delete=models.CASCADE)