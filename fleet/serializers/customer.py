from rest_framework import serializers

from fleet.models import Customer, User

from .user import UserSerializer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer pour le model Customer
    """

    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = (
            "user",
            "logo",
            "is_archived",
            "is_active",
            "featured_campaign",
            "featured_game",
        )


class CustomerSerializerWithUser(CustomerSerializer):
    """
    Serializer pour le model Customer with its user
    """

    user = UserSerializer()

    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = (
            "user",
            "logo",
            "is_archived",
            "is_active",
            "featured_campaign",
            "featured_game",
        )

    def create(self, validated_data):
        user_data = validated_data.pop("user")

        user = User.objects.create(**user_data)

        try:
            customer = Customer.objects.create(
                user=user,
                **validated_data,
            )

            return customer

        except Exception as e:
            user.delete()
            raise e


class UserSerializerWithCustomer(serializers.ModelSerializer):
    """
    Serializer pour le model User including its customer as read_only
    """

    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = User
        fields = "__all__"
