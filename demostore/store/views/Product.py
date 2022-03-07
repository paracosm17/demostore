from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

from store.models import Product, Category
from store.serializers.Product import ProductSerializer, ProductCreateSerializer

def validate_id(id):
    if id:
        return id.isdigit()
    return False

class ProductApi(APIView):
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
