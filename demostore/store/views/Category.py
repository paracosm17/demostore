from rest_framework.views import APIView
from rest_framework.response import Response
from store.models import Category
from store.serializers.Category import CategorySerializer

def validate_id(id):
    if id:
        return id.isdigit()
    return False


class CategoryApi(APIView):
    '''
    View for all categories
    '''
    def get(self, request, *args, **kwargs):
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
