from rest_framework import serializers

from screensaver.serializers.screensaver_broadcast import ScreenSaverBroadcastSerializer

from fleet.models import Campaign, Customer, User
from fleet.serializers import (
    CampaignSerializer,
    UserSerializerWithCustomer,
    CustomerSerializer,
)

from game.serializers import GameSerializer
from game.models import Game

from .models import Terminal, Donator, Session, Payment


# Serializer pour le model Donator
class DonatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donator
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentForTerminalSerializer(serializers.ModelSerializer):
    donator = DonatorSerializer(many=False, read_only=True)
    campaign = CampaignSerializer(many=False, read_only=True)
    game = GameSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


# Serializer pour le model Terminal
class FullTerminalSerializer(serializers.ModelSerializer):
    """
    This serialize all data of a terminal.
    It is intended TO BE USED WITH SETH and serialize all data that could be read or edit by admin or customer from Seth
    (including terminal owner, terminal customer, all screensavers...)
    """

    owner = UserSerializerWithCustomer(many=False)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="owner"
    )

    customer = CustomerSerializer(many=False)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), write_only=True, source="customer"
    )

    campaigns = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(), many=True, allow_null=True
    )
    games = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(), many=True, allow_null=True
    )
    subscription_type = serializers.ReadOnlyField()
    payment_terminal = serializers.CharField(allow_null=True)
    donation_formula = serializers.CharField()
    screensaver_broadcasts = ScreenSaverBroadcastSerializer(
        many=True,
        read_only=True,
    )
    total_donations = serializers.ReadOnlyField()
    payments = PaymentForTerminalSerializer(many=True, read_only=True)
    avg_donation = serializers.ReadOnlyField()
    avg_timesession = serializers.ReadOnlyField()
    avg_gametimesession = serializers.ReadOnlyField()
    subscription_type = serializers.ReadOnlyField()

    class Meta:
        model = Terminal
        fields = "__all__"


class LightTerminalSerializer(serializers.ModelSerializer):
    """
    This serialize ONLY STRICTLY NECESSARY DATA FOR HERA.
    It should serialize only public data as it will be sent to Hera, NO SENSIBLE DATA !
    (for example, only visible screensavers, not all of them)
    """

    campaigns = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(), many=True, allow_null=True
    )
    games = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(), many=True, allow_null=True
    )
    subscription_type = serializers.ReadOnlyField()
    payment_terminal = serializers.CharField(allow_null=True)
    donation_formula = serializers.CharField()
    screensaver_broadcasts = ScreenSaverBroadcastSerializer(
        many=True,
        read_only=True,
        source="visible_screensaver_broadcasts",
    )

    class _CustomerSerializer(serializers.ModelSerializer):
        class Meta:
            model = Customer
            fields = ("company",)

    customer = _CustomerSerializer(read_only=True)

    class Meta:
        model = Terminal
        fields = "__all__"


# Serializer pour le model Terminal
class TerminalSemiSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    location = serializers.CharField()
    is_active = serializers.BooleanField()
    is_on = serializers.BooleanField()
    is_playing = serializers.BooleanField()
    play_timer = serializers.IntegerField()
    campaigns = CampaignSerializer(many=True, allow_null=True)
    games = GameSerializer(many=True, allow_null=True)
    owner = UserSerializerWithCustomer(many=False, read_only=True)
    customer = CustomerSerializer(many=False, read_only=True)
    total_donations = serializers.ReadOnlyField()
    avg_donation = serializers.ReadOnlyField()
    avg_timesession = serializers.ReadOnlyField()
    avg_gametimesession = serializers.ReadOnlyField()
    subscription_type = serializers.ReadOnlyField()
    free_mode_text = serializers.CharField()
    payment_terminal = serializers.CharField(allow_null=True)
    donation_formula = serializers.CharField(allow_null=True)


# Serializer pour le model Terminal
class TerminalFullSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    location = serializers.CharField()
    is_active = serializers.BooleanField()
    is_on = serializers.BooleanField()
    is_playing = serializers.BooleanField()
    play_timer = serializers.IntegerField()
    campaigns = CampaignSerializer(many=True, allow_null=True)
    games = GameSerializer(many=True, allow_null=True)
    owner = UserSerializerWithCustomer(many=False, read_only=True)
    customer = CustomerSerializer(many=False, read_only=True)
    total_donations = serializers.ReadOnlyField()
    payments = PaymentForTerminalSerializer(many=True, read_only=True)
    avg_donation = serializers.ReadOnlyField()
    avg_timesession = serializers.ReadOnlyField()
    avg_gametimesession = serializers.ReadOnlyField()
    subscription_type = serializers.ReadOnlyField()
    free_mode_text = serializers.CharField()
    payment_terminal = serializers.CharField(allow_null=True)
    donation_formula = serializers.CharField()


# Serializer pour le model Payment
class PaymentFullSerializer(serializers.ModelSerializer):
    donator = DonatorSerializer(many=False, read_only=True)
    campaign = CampaignSerializer(many=False, read_only=True)
    terminal = FullTerminalSerializer(many=False, read_only=True)
    game = GameSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


# Serializer pour le model Session
# On surcharge la méthode "Create" pour calculer les timesessions
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = "__all__"

    def create(self, validated_data):
        if (
            validated_data["end_time"]
            and validated_data["start_time"]
            and validated_data["end_global"]
            and validated_data["start_global"]
        ):
            validated_data["timesession"] = (
                validated_data["end_time"] - validated_data["start_time"]
            )
            validated_data["timesession_global"] = (
                validated_data["end_global"] - validated_data["start_global"]
            )
        else:
            validated_data["timesession"] = None
            validated_data["timesession_global"] = None
        session = Session.objects.create(**validated_data)
        session.save()
        return session

    def update(self, instance, validated_data):
        if (
            validated_data["end_time"]
            and validated_data["start_time"]
            and validated_data["end_global"]
            and validated_data["start_global"]
        ):
            validated_data["timesession"] = (
                validated_data["end_time"] - validated_data["start_time"]
            )
            validated_data["timesession_global"] = (
                validated_data["end_global"] - validated_data["start_global"]
            )
        else:
            validated_data["timesession"] = None
            validated_data["timesession_global"] = None
        instance = super().update(instance, validated_data)
        return instance
