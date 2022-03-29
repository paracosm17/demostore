from rest_framework import serializers

from store.models import Appeal


class AppealSerializer(serializers.ModelSerializer):
    '''
    Serializer for model Appeal
    '''

    class Meta:
        model = Appeal
        fields = ['id', 'user', 'text', 'viewed', 'status', 'added']


class AppealCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = ('user', 'text',)

    def create(self, validated_data):
        return Appeal.objects.create(**validated_data)
