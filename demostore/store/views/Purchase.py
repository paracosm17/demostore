from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from store.models import TgUser, Product, Category, Purchase
from store.serializers.PurchaseAndTgUser import PurchaseSerializer, PurchaseCreateSerializer, PurchaseSerializerWithBuyer

def validate_id(id):
    if id:
        return id.isdigit()
    return False

class PurchaseApi(APIView):
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
                serialized_all_purchase = PurchaseSerializerWithBuyer(all_purchase, context={"request": request}, many=True)
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
    
    def post(self, request):
        purchase = request.data
        buyer_id = TgUser.objects.get(user_id=purchase['buyer']).id
        purchase['buyer'] = buyer_id
        serializer = PurchaseCreateSerializer(data=purchase)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})
