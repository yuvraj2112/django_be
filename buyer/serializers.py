from rest_framework import serializers
from buyer.models import Buyer, Order
import uuid

class BuyerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mobile = serializers.CharField(max_length=10, allow_blank=False)
    slug = serializers.SlugField(max_length=36, default=uuid.uuid4, read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Seller` instance, given the validated data.
        """
        return Buyer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance

class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    store_id = serializers.IntegerField(required=True)
    customer_id = serializers.IntegerField(required=True)
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.store_id = validated_data.get('store_id', instance.store_id)
        instance.customer_id = validated_data.get('customer_id', instance.customer_id)
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance