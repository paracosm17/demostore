from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from store.models import Category
from store.serializers.Category import CategorySerializer

def validate_page(page):
    if page:
        return page.isdigit()
    return False


class CategoryApi(APIView):
    '''
    View for all categories
    '''
    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page')
        if validate_page(page) and int(page) > 0:
            page = int(page)
            all_category = Category.objects.all()
            paginator = Paginator(all_category, 5)
            if page == 1 or paginator.page(page-1).has_next():
                serialized_page_category = CategorySerializer(paginator.page(page), 
                context={"request": request}, many=True)
                return Response(serialized_page_category.data)
            raise serializers.ValidationError(f"This page does not exist! The last page is {paginator.num_pages}")
        # Return all serialized categories
        all_category = Category.objects.all()
        serialized_all_category = CategorySerializer(all_category, context={"request": request}, many=True)
        return Response(serialized_all_category.data)

    def post(self, request):
        category = request.data
        serializer = CategorySerializer(data=category)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})
