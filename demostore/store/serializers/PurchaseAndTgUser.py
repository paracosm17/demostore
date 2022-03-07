from rest_framework import serializers
from store.models import Purchase, TgUser
from store.serializers.Product import ProductSerializer

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


class PurchaseSerializerWithBuyer(serializers.ModelSerializer):
    '''
    Serializer for model Purchase (With buyer)
    '''
    sum = serializers.SerializerMethodField('get_total_sum')
    buyer = TgUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'sum', 'status', 'added']
    def get_total_sum(self, obj):
        return obj.product.price * obj.quantity


class PurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'status']
    
    def create(self, validated_data):
        return Purchase.objects.create(**validated_data)
        

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
        