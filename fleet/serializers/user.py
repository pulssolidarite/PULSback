from rest_framework import serializers
from fleet.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le model User
    """

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        obj = User.objects.create_user(
            validated_data["username"], "", validated_data["password"]
        )
        obj.save()
        return obj
