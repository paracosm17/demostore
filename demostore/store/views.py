import decimal

from django.core.paginator import Paginator
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Appeal
from store.models import Product, Category, Purchase
from store.models import TgUser
from store.serializers import AppealSerializer, AppealCreateSerializer
from store.serializers import CategorySerializer
from store.serializers import ProductSerializer, ProductCreateSerializer
from store.serializers import PurchaseCreateSerializer, PurchaseSerializerWithBuyer
from store.serializers import TgUserSerializer, TgUserSerializerWithPurchases


def validate_integer(integer: str) -> bool:
    if integer:
        return integer.isdigit()
    return False


class AppealApi(APIView):
    """ Api view for appeals 
    _summary_

    Args:
        APIView (_type_): _description_

    Raises:
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        appeal_id = request.query_params.get('id')

        if validate_integer(user_id):
            user_id = int(user_id)
            if user_id in [t.user_id for t in TgUser.objects.all()]:
                all_appeal = Appeal.objects.filter(user__user_id=user_id)
                serialized_all_appeal = AppealSerializer(all_appeal, context={"request": request}, many=True)
                return Response(serialized_all_appeal.data)
            raise serializers.ValidationError("This user does not exist!")

        if validate_integer(appeal_id):
            appeal_id = int(appeal_id)
            if appeal_id in [a.id for a in Appeal.objects.all()]:
                all_appeal = Appeal.objects.get(id=appeal_id)
                serialized_all_purchase = AppealSerializer(all_appeal, context={"request": request})
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This appeal does not exist!")

        # If there are no query params, return all appeals
        all_appeal = Appeal.objects.all()
        serialized_all_purchase = AppealSerializer(all_appeal, context={"request": request}, many=True)
        return Response(serialized_all_purchase.data)

    def post(self, request):
        appeal = request.data
        user_id = TgUser.objects.get(user_id=appeal['user_id']).id
        appeal['user'] = user_id
        serializer = AppealCreateSerializer(data=appeal)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class CategoryApi(APIView):
    """ Api view for categories
    _summary_

    Args:
        APIView (_type_): _description_

    Raises:
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page')
        category_id = request.query_params.get('id')

        if validate_integer(category_id):
            category_id = int(category_id)
            if category_id in [c.id for c in Category.objects.all()]:
                serialized_category = CategorySerializer(Category.objects.get(id=category_id),
                                                         context={"request": request}, many=False)
                return Response(serialized_category.data)
            raise serializers.ValidationError("This category does not exist!")

        all_category = Category.objects.all()
        paginator = Paginator(all_category, 5)
        if validate_integer(page) and int(page) > 0:
            page = int(page)
            if page == 1 or paginator.page(page - 1).has_next():
                serialized_page_category = CategorySerializer(paginator.page(page),
                                                              context={"request": request}, many=True)
                return Response({"pages": paginator.num_pages, "categories": serialized_page_category.data})
            raise serializers.ValidationError(f"This page does not exist! The last page is {paginator.num_pages}")

        # Return all serialized categories
        serialized_all_category = CategorySerializer(all_category, context={"request": request}, many=True)
        return Response({"pages": paginator.num_pages, "categories": serialized_all_category.data})

    def post(self, request):
        category = request.data
        serializer = CategorySerializer(data=category)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class ProductApi(APIView):
    """ Api view for products
    _summary_

    Args:
        APIView (_type_): _description_

    Raises:
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('id')
        category = request.query_params.get('category')
        all = request.query_params.get('all')
        page = request.query_params.get('page')
        products = Product.objects.exclude(quantity=0)

        if validate_integer(product_id):
            # If query param 'id' is valid, will return
            # one serialized Product model by id
            product_id = int(product_id)
            if product_id in [p.id for p in Product.objects.all()]:
                product = Product.objects.get(id=product_id)
                serialized_product = ProductSerializer(product, context={"request": request}, many=False)
                return Response(serialized_product.data)
            raise serializers.ValidationError("This product does not exist!")

        if all in ['True', 'true', '1']:
            # If query param 'all' is valid, will return
            # all serialized Products
            products = Product.objects.all()
        elif all and all not in ['True', 'true', '1']:
            raise serializers.ValidationError("Param all must be 'true', 'True' or '1'")

        if validate_integer(category):
            # If query param 'category' is valid, will return
            # products by category id
            category = int(category)
            if category in [p.id for p in Category.objects.all()]:
                products = products.filter(category__id=category)
            else:
                raise serializers.ValidationError("This category does not exist!")

        if validate_integer(page) and int(page) > 0:
            page = int(page)
            paginator = Paginator(products, 5)
            if page == 1 or paginator.page(page - 1).has_next():
                serialized_page_product = ProductSerializer(paginator.page(page),
                                                            context={"request": request}, many=True)
                return Response({"pages": paginator.num_pages, "products": serialized_page_product.data})
            else:
                raise serializers.ValidationError(f"This page does not exist! The last page is {paginator.num_pages}")

        # If there are no query params, return products, whose quantity is greater than zero  
        serialized_product = ProductSerializer(products, context={"request": request}, many=True)
        return Response(serialized_product.data)

    def post(self, request):
        product = request.data
        try:
            category_id = Category.objects.get(name=product['category']['name']).id
        except:
            category_id = Category.objects.create(name=product['category']['name']).id
        product['category'] = category_id
        serializer = ProductCreateSerializer(data=product)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class PurchaseApi(APIView):
    """ Api view for purchases
    _summary_

    Args:
        APIView (_type_): _description_

    Raises:
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        product_id = request.query_params.get('product_id')
        category_id = request.query_params.get('category_id')
        if validate_integer(user_id):
            # If query param 'user_id' is valid, will return
            # serialized user's purchases
            user_id = int(user_id)
            if user_id in [t.user_id for t in TgUser.objects.all()]:
                all_purchase = Purchase.objects.filter(buyer__user_id=user_id)
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request},
                                                                      many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This user does not exist!")
        if validate_integer(product_id):
            # If query param 'product_id' is valid, will return
            # all serialized purchases by product
            product_id = int(product_id)
            if product_id in [t.id for t in Product.objects.all()]:
                all_purchase = Purchase.objects.filter(product__id=product_id)
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request},
                                                                      many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This product does not exist!")
        if validate_integer(category_id):
            # If query param 'category_id' is valid, will return
            # all serialized purchases by category
            category_id = int(category_id)
            if category_id in [t.id for t in Category.objects.all()]:
                all_purchase = Purchase.objects.filter(product__category__id=category_id)
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request},
                                                                      many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This category does not exist!")

        # If there are no query params, return all purchases 
        all_purchase = Purchase.objects.all()
        serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request}, many=True)
        return Response(serialized_all_purchase.data)

    def post(self, request):
        purchase = request.data
        buyer_id = TgUser.objects.get(user_id=purchase['buyer']).id
        purchase['buyer'] = buyer_id
        serializer = PurchaseCreateSerializer(data=purchase)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class TgUserApi(APIView):
    """ Api view for tgusers
    _summary_

    Args:
        APIView (_type_): _description_

    Raises:
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if validate_integer(user_id):
            # If query param 'user_id' is valid, will return
            # serialized TgUser object, with him purchases
            user_id = int(user_id)
            if user_id in [u.user_id for u in TgUser.objects.all()]:
                user = TgUser.objects.get(user_id=int(user_id))
                serialized_user = TgUserSerializerWithPurchases(user, context={"request": request}, many=False)
                return Response(serialized_user.data)
            raise serializers.ValidationError("User does not exist!")
        # If there are no query params, return all users, without their purchases
        users = TgUser.objects.all()
        serialized_user = TgUserSerializer(users, context={"request": request}, many=True)
        return Response(serialized_user.data)

    def post(self, request):
        user = request.data
        serializer = TgUserSerializer(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class TgUserUpdate(generics.UpdateAPIView):
    """ Api view for tgusers (update)
    _summary_

    Args:
        generics (_type_): _description_

    Raises:
        serializers.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    permission_classes = (IsAuthenticated,)
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer

    def update(self, request, *args, **kwargs):
        instance = TgUser.objects.get(user_id=request.data.get("user_id"))
        phone, email = request.data.get("phone"), request.data.get("email")
        increase_bal, decrease_bal = request.data.get("increase_bal"), request.data.get("decrease_bal")
        if phone or email or increase_bal or decrease_bal:
            if phone:
                instance.phone = request.data.get("phone")
            if email:
                instance.email = request.data.get("email")
            if increase_bal:
                increase_bal = decimal.Decimal(increase_bal)
                instance.balance += increase_bal
            if decrease_bal:
                decrease_bal = decimal.Decimal(decrease_bal)
                instance.balance -= decrease_bal
            instance.save()
            return Response({'status': 200})
        raise serializers.ValidationError("You haven't updated anything")
