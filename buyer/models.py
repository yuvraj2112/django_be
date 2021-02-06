from django.db import models
from seller.models import Store, Product
import uuid


class Buyer(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    mobile = models.CharField(max_length=10, blank=False)
    slug = models.SlugField(max_length=36, default=uuid.uuid4, editable=False)

class Order(models.Model):
    store = models.ForeignKey(Store, default=None, on_delete=models.CASCADE)
    customer = models.ForeignKey(Buyer, default=None, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, default=1)
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
