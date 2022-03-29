from django.core.paginator import Paginator
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Product, Category
from store.serializers.Product import ProductSerializer, ProductCreateSerializer


def validate_integer(integer: str) -> bool:
    if integer:
        return integer.isdigit()
    return False


class ProductApi(APIView):
    """
    View for products
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('id')
        category = request.query_params.get('category')
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
