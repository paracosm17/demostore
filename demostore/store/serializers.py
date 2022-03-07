from rest_framework import serializers
from store.models import Category, TgUser, Product, Purchase

class CategorySerializer(serializers.ModelSerializer):
    '''
    Serializer for model Category
    '''
    class Meta:
        model = Category
        fields = ['id', 'name']


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


class PurchaseSerializer(serializers.ModelSerializer):
    '''
    Serializer for model Purchase
    '''
    sum = serializers.SerializerMethodField('get_total_sum')
    buyerTgId = serializers.SerializerMethodField('get_buyer_tg_id')
    class Meta:
        model = Purchase
        fields = ['buyer', 'buyerTgId', 'product', 'quantity', 'sum', 'status', 'added']
    
    def get_total_sum(self, obj):
        return obj.product.price * obj.quantity
    
    def get_buyer_tg_id(self, obj):
        return obj.buyer.user_id

class TgUserSerializer(serializers.ModelSerializer):
    '''
    Serializer for model TgUser
    '''
    class Meta:
        model = TgUser
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'balance', 'language_code', 'phone', 'email']

    def create(self, validated_data):
        return TgUser.objects.create(**validated_data)
    
    def update(self, validated_data):
        instanse = TgUser.objects.get(user_id=validated_data["user_id"])
        return TgUserSerializer(instanse, data=validated_data, partial=True)

class TgUserSerializerWithPurchases(serializers.ModelSerializer):
    '''
    Serializer for model TgUser (With full purchases)
    '''
    purchases = serializers.SerializerMethodField('get_purchases')
    class Meta:
        model = TgUser
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'balance', 'language_code', 'phone', 'email', 'purchases']
    
    def get_purchases(self, obj): 
        return PurchaseSerializer(Purchase.objects.filter(buyer__id=obj.id), many=True).data


class PurchaseSerializerWithBuyer(serializers.ModelSerializer):
    '''
    Serializer for model Purchase (With buyer)
    '''
    buyer = TgUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'status', 'added']


class PurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'status']
    
    def create(self, validated_data):
        return Purchase.objects.create(**validated_data)


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'quantity']
    
    def create(self, validated_data):
        return Product.objects.create(**validated_data)
        