from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from fleet.models import Campaign, Customer, User
from fleet.serializers import (
    CampaignSerializer,
    CustomerSerializer,
    UserSerializerWithCustomer,
)
from game.models import Game
from screensaver.serializers.screensaver_broadcast import ScreenSaverBroadcastSerializer

from .models import Donator, Payment, Session, Terminal


class _GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            "id",
            "name",
        )


# Serializer pour le model Donator
class _DonatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donator
        fields = "__all__"


class _CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
        )


class PaymentForTerminalSerializer(serializers.ModelSerializer):
    donator = _DonatorSerializer(many=False, read_only=True)
    campaign = _CampaignSerializer(many=False, read_only=True)
    game = _GameSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


class _SimpleUserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le model User
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
        )
        extra_kwargs = {"id": {"read_only": True}, "password": {"write_only": True}}


# Serializer pour le model Terminal
class FullTerminalSerializer(serializers.ModelSerializer):
    """
    This serialize all data of a terminal.
    It is intended TO BE USED WITH SETH and serialize all data that could be read or edit by admin or customer from Seth
    (including terminal owner, terminal customer, all screensavers...)
    """

    owner = _SimpleUserSerializer()
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="owner", required=False
    )

    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        write_only=True,
        source="customer",
        required=False,
    )

    campaigns = _CampaignSerializer(many=True, read_only=True)
    campaign_ids = serializers.PrimaryKeyRelatedField(
        queryset=Campaign.objects.all(), many=True, source="campaigns", required=False
    )

    games = _GameSerializer(many=True, read_only=True)
    game_ids = serializers.PrimaryKeyRelatedField(
        queryset=Game.objects.all(), many=True, source="games", required=False
    )

    payment_terminal = serializers.CharField(allow_null=True)
    donation_formula = serializers.CharField()

    # Other read only stuffs

    subscription_type = serializers.ReadOnlyField()
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

    def create(self, validated_data):
        # Parse data

        customer = validated_data.pop("customer", None)
        owner = validated_data.pop("owner", None)
        campaigns = validated_data.pop("campaigns", None)
        games = validated_data.pop("games", None)

        # Create customer if needed

        if customer is None:
            raise ValidationError(
                {
                    "customer",
                    "customer or customer_id required",
                    "customer_id",
                    "customer or customer_id required",
                }
            )

        if customer is not None and not isinstance(customer, Customer):
            # Create new customer
            customer_serializer = CustomerSerializer(data=customer)
            if not customer_serializer.is_valid():
                raise ValidationError(customer_serializer.errors)
            customer = customer_serializer.save()

        # Create owner if needed

        if owner is None:
            raise ValidationError(
                {
                    "owner",
                    "owner or owner_id required",
                    "owner_id",
                    "owner or owner_id required",
                }
            )

        if owner is not None and not isinstance(owner, User):
            # Create new owner
            owner_serializer = _SimpleUserSerializer(data=owner)
            if not owner_serializer.is_valid():
                raise ValidationError(owner_serializer.errors)
            owner = owner_serializer.save()

        # Create terminal

        terminal: Terminal = Terminal.objects.create(
            **validated_data,
            customer=customer,
            owner=owner,
        )

        # Assign campaigns

        if campaigns:
            terminal.campaigns.set(campaigns)

        # Assign games

        if games:
            terminal.games.set(games)

        # Return

        return terminal


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
        source="get_visible_screensaver_broadcasts",
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
    games = _GameSerializer(many=True, allow_null=True)
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
    version = serializers.CharField(read_only=True)


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
    games = _GameSerializer(many=True, allow_null=True)
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
    donator = _DonatorSerializer(many=False, read_only=True)
    campaign = CampaignSerializer(many=False, read_only=True)
    terminal = FullTerminalSerializer(many=False, read_only=True)
    game = _GameSerializer(many=False, read_only=True)

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
