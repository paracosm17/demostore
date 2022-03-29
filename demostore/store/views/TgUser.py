import decimal

from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from store.models import TgUser
from store.serializers.PurchaseAndTgUser import TgUserSerializer, TgUserSerializerWithPurchases


def validate_integer(integer: str) -> bool:
    if integer:
        return integer.isdigit()
    return False


class TgUserApi(APIView):
    """
    View for telegram users
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if validate_integer(user_id):
            # If query param 'user_id' is valid, will return
            # serialized TgUser object, with him purchases
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

    def post(self, request):
        user = request.data
        serializer = TgUserSerializer(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"status": 200})


class TgUserUpdate(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TgUser.objects.all()
    serializer_class = TgUserSerializer

    def update(self, request, *args, **kwargs):
        instance = TgUser.objects.get(user_id=request.data.get("user_id"))
        phone, email = request.data.get("phone"), request.data.get("email")
        increase_bal, decrease_bal = request.data.get("increase_bal"), request.data.get("decrease_bal")
        if phone or email or increase_bal or decrease_bal:
            if phone:
                instance.phone = request.data.get("phone")
            if email:
                instance.email = request.data.get("email")
            if increase_bal:
                increase_bal = decimal.Decimal(increase_bal)
                instance.balance += increase_bal
            if decrease_bal:
                decrease_bal = decimal.Decimal(decrease_bal)
                instance.balance -= decrease_bal
            instance.save()
            return Response({'status': 200})
        raise serializers.ValidationError("You haven't updated anything")
