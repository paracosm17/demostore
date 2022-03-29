from rest_framework import serializers

from store.models import Category


class CategorySerializer(serializers.ModelSerializer):
    '''
    Serializer for model Category
    '''

    class Meta:
        model = Category
        fields = ['id', 'name']
