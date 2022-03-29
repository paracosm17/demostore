from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import Appeal, TgUser
from store.serializers.Appeal import AppealSerializer, AppealCreateSerializer


def validate_integer(integer: str) -> bool:
    if integer:
        return integer.isdigit()
    return False


class AppealApi(APIView):
    """
    View for appeal
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
        user_id = TgUser.objects.get(user_id=appeal['user']).id
        appeal['user'] = user_id
        serializer = AppealCreateSerializer(data=appeal)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})
