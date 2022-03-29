from django.core.paginator import Paginator
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Category
from store.serializers.Category import CategorySerializer


def validate_integer(integer: str) -> bool:
    if integer:
        return integer.isdigit()
    return False


class CategoryApi(APIView):
    """
    View for all categories
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
