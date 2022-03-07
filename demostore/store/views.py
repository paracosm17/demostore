from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, generics

from store.serializers import (ProductCreateSerializer, TgUserSerializer, ProductSerializer, CategorySerializer, 
PurchaseSerializer, PurchaseSerializerWithBuyer, TgUserSerializerWithPurchases, PurchaseCreateSerializer)
from store.models import TgUser, Product, Category, Purchase

def validate_id(id):
    if id:
        return id.isdigit()
    return False


class CategoriesApi(APIView):
    '''
    View for all categories
    '''
    def get(self, request, *args, **kwargs):
        # Return all serialized categories
        all_category = Category.objects.all()
        serialized_all_category = CategorySerializer(all_category, context={"request": request}, many=True)
        return Response(serialized_all_category.data)


class PurchasesApi(APIView):
    '''
    View for purchases
    '''
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        product_id = request.query_params.get('product_id')
        category_id = request.query_params.get('category_id')
        if validate_id(user_id):
            # If query param 'user_id' is valid, will return
            # serialized user's purchases
            user_id = int(user_id)
            if user_id in [t.user_id for t in TgUser.objects.all()]:
                all_purchase = Purchase.objects.filter(buyer__user_id=user_id)
                serialized_all_purchase = PurchaseSerializer(all_purchase, context={"request": request}, many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This user does not exist!")
        if validate_id(product_id):
            # If query param 'product_id' is valid, will return
            # all serialized purchases by product
            product_id = int(product_id)
            if product_id in [t.id for t in Product.objects.all()]:
                all_purchase = Purchase.objects.filter(product__id=product_id)
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request}, many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This product does not exist!")
        if validate_id(category_id):
            # If query param 'category_id' is valid, will return
            # all serialized purchases by category
            category_id = int(category_id)
            if category_id in [t.id for t in Category.objects.all()]:
                all_purchase = Purchase.objects.filter(product__category__id=category_id)
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request}, many=True)
                return Response(serialized_all_purchase.data)
            raise serializers.ValidationError("This category does not exist!")
        
        # If there are no query params, return all purchases 
        all_purchase = Purchase.objects.all()
        serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request}, many=True)
        return Response(serialized_all_purchase.data)    


class TgUsersApi(APIView):
    '''
    View for telegram users
    '''
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')        
        if validate_id(user_id):
            # If query param 'user_id' is valid, will return
            # serialized TgUser object, with him's purchases
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
        

class ProductsApi(APIView):
    '''
    View for products
    '''
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        category = request.query_params.get('category')
        all = request.query_params.get('all')

        if validate_id(id):
            # If query param 'id' is valid, will return
            # one serialized Product model by id
            id = int(id)
            if id in [p.id for p in Product.objects.all()]:
                product = Product.objects.get(id=id)
                serialized_product = ProductSerializer(product, context={"request": request}, many=False)
                return Response(serialized_product.data)
            raise serializers.ValidationError("This product does not exist!")
        
        if validate_id(category):
            # If query param 'category' is valid, will return
            # products by category id
            category = int(category)
            if category in [p.id for p in Category.objects.all()]:
                products = Product.objects.filter(category__id=category)
                if all not in ['True', 'true', '1']:
                    products = products.exclude(quantity=0)
                serialized_products = ProductSerializer(products, context={"request": request}, many=True)
                return Response(serialized_products.data)
            raise serializers.ValidationError("This category does not exist!")
       
        if all in ['True', 'true', '1']:
            # If query param 'all' is valid, will return
            # all serialized Products
            products = Product.objects.all()
            serialized_products = ProductSerializer(products, context={"request": request}, many=True)
            return Response(serialized_products.data)
        elif all and all not in ['True', 'true', '1']:
            raise serializers.ValidationError("Param all must be 'true', 'True' or '1'")
        
        # If there are no query params, return products, whose quantity is greater than zero  
        product = Product.objects.exclude(quantity=0)
        serialized_product = ProductSerializer(product, context={"request": request}, many=True)
        return Response(serialized_product.data)
    
    
class CategoryCreate(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 200,
            'message': 'Category added',
            'data': response.data
        })


class TgUserApi(APIView):
    def post(self, request):
        user = request.data
        serializer = TgUserSerializer(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})
    

class PurchaseCreate(APIView):
    def post(self, request):
        purchase = request.data
        buyer_id = TgUser.objects.get(user_id = purchase['buyer']['tgId']).id
        purchase['buyer'] = buyer_id
        serializer = PurchaseCreateSerializer(data=purchase)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})

class ProductCreate(APIView):
    def post(self, request):
        product = request.data
        try:
            category_id = Category.objects.get(name = product['category']['name']).id
        except:
            category_id = Category.objects.create(name = product['category']['name']).id
        product['category'] = category_id
        serializer = ProductCreateSerializer(data=product)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})
