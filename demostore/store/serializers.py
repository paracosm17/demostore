from rest_framework import serializers

from store.models import Appeal
from store.models import Category
from store.models import Product
from store.models import Purchase, TgUser


class AppealSerializer(serializers.ModelSerializer):
    """ Serializer for model Appeal
    _summary_

    Args:
        serializers (_type_): _description_
    """

    class Meta:
        model = Appeal
        fields = ['id', 'user', 'text', 'viewed', 'status', 'added']


class AppealCreateSerializer(serializers.ModelSerializer):
    """_summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = Appeal
        fields = ('user', 'text',)

    def create(self, validated_data):
        return Appeal.objects.create(**validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """ Serializer for model Category
    _summary_

    Args:
        serializers (_type_): _description_
    """

    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    """ Serializer for model Product
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
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
    """ Serializer for model Product (for create)
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'quantity']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)


class PurchaseSerializer(serializers.ModelSerializer):
    """ Serializer for model Purchase
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    sum = serializers.SerializerMethodField('get_total_sum')
    buyerTgId = serializers.SerializerMethodField('get_buyer_tg_id')

    class Meta:
        model = Purchase
        fields = ['buyer', 'buyerTgId', 'product', 'quantity', 'sum', 'status', 'added']

    @staticmethod
    def get_total_sum(obj):
        return obj.product.price * obj.quantity

    @staticmethod
    def get_buyer_tg_id(obj):
        return obj.buyer.user_id


class TgUserSerializer(serializers.ModelSerializer):
    """ Serializer for model TgUser
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """

    class Meta:
        model = TgUser
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'balance', 'language_code', 'phone', 'email']

    def create(self, validated_data):
        return TgUser.objects.create(**validated_data)


class PurchaseSerializerWithBuyer(serializers.ModelSerializer):
    """ Serializer for model Purchase (With buyer)
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    sum = serializers.SerializerMethodField('get_total_sum')
    buyer = TgUserSerializer()
    product = ProductSerializer()

    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'sum', 'status', 'added']

    @staticmethod
    def get_total_sum(obj):
        return obj.product.price * obj.quantity


class PurchaseCreateSerializer(serializers.ModelSerializer):
    """ Serializer for model Purchase (for create)
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = Purchase
        fields = ['buyer', 'product', 'quantity', 'status']

    def create(self, validated_data):
        return Purchase.objects.create(**validated_data)


class TgUserSerializerWithPurchases(serializers.ModelSerializer):
    """ Serializer for model TgUser (With full purchases)
    _summary_

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    purchases = serializers.SerializerMethodField('get_purchases')

    class Meta:
        model = TgUser
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'balance', 'language_code', 'phone', 'email',
                  'purchases']

    @staticmethod
    def get_purchases(obj):
        return PurchaseSerializer(Purchase.objects.filter(buyer__id=obj.id), many=True).data
