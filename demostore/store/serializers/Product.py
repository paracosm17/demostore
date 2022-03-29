from rest_framework import serializers

from store.models import Product
from store.serializers.Category import CategorySerializer


class ProductSerializer(serializers.ModelSerializer):
    '''
    Serializer for model Product
    '''
    image_url = serializers.SerializerMethodField('get_image_url')
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'quantity', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url)

    def get_category_name(self, obj):
        return obj.category.name


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'quantity']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)
