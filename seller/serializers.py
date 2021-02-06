from rest_framework import serializers
from seller.models import Seller, Login, Store, Category, Product
import uuid

class SellerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, allow_blank=True, required=False, default='')
    mobile = serializers.CharField(max_length=10, allow_blank=False)
    slug = serializers.SlugField(max_length=36, default=uuid.uuid4, read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Seller` instance, given the validated data.
        """
        return Seller.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    mobile = serializers.CharField(max_length=10, allow_blank=False)
    otp = serializers.CharField(max_length=4, allow_blank=False)

    def create(self, validated_data):
        return Login.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.otp = validated_data.get('otp', instance.otp)
        instance.save()
        return instance

class StoreSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, allow_blank=False)
    address = serializers.CharField(allow_blank=False)
    slug = serializers.SlugField(max_length=36, default=uuid.uuid4, read_only=True)
    seller_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return Store.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.seller_id = validated_data.get('seller_id', instance.seller_id)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.save()
        return instance

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200, default='', allow_blank=False)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200, allow_blank=False)
    description = serializers.CharField(default='', allow_blank=True, required=False)
    mrp = serializers.IntegerField( default=0)
    sale_price = serializers.IntegerField( default=0)
    count = serializers.IntegerField( default=0)
    category_id = serializers.IntegerField(required=True)
    seller_id = serializers.IntegerField(required=True)
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.mrp = validated_data.get('mrp', instance.mrp)
        instance.sale_price = validated_data.get('sale_price', instance.sale_price)
        instance.count = validated_data.get('count', instance.count)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.seller_id = validated_data.get('seller_id', instance.seller_id)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
