import datetime
from rest_framework import serializers
from .models import Terminal, Donator, Session, Payment, Game
from fleet.models import Campaign
from fleet.serializers import CampaignSerializer, UserFullSerializer


# Serializer pour le model Terminal
class GameSerializer(serializers.ModelSerializer):
    nb_terminals = serializers.ReadOnlyField()
    total_donations = serializers.ReadOnlyField()

    class Meta:
        model = Game
        fields = '__all__'

    def get_logo_url(self, game):
        if game.logo:
            if self.context.get('request'):
                request = self.context.get('request')
                logo_url = game.logo.url
                return request.build_absolute_uri(logo_url)
            else:
                return game.logo.url
        else:
            return game.logo


# Serializer pour le model Donator
class DonatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donator
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentForTerminalSerializer(serializers.ModelSerializer):
    donator = DonatorSerializer(many=False, read_only=True)
    campaign = CampaignSerializer(many=False, read_only=True)
    game = GameSerializer(many=False, read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'


# Serializer pour le model Terminal
class TerminalSerializer(serializers.ModelSerializer):
    campaigns = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), many=True, allow_null=True)
    games = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), many=True, allow_null=True)
    #owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Terminal
        fields = '__all__'


# Serializer pour le model Terminal
class TerminalSemiSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    location = serializers.CharField()
    is_active = serializers.BooleanField()
    is_on = serializers.BooleanField()
    is_playing = serializers.BooleanField()
    campaigns = CampaignSerializer(many=True, allow_null=True)
    games = GameSerializer(many=True, allow_null=True)
    owner = UserFullSerializer(many=False, read_only=True)
    total_donations = serializers.ReadOnlyField()
    avg_donation = serializers.ReadOnlyField()
    avg_timesession = serializers.ReadOnlyField()
    avg_gametimesession = serializers.ReadOnlyField()


# Serializer pour le model Terminal
class TerminalFullSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    location = serializers.CharField()
    is_active = serializers.BooleanField()
    is_on = serializers.BooleanField()
    is_playing = serializers.BooleanField()
    campaigns = CampaignSerializer(many=True, allow_null=True)
    games = GameSerializer(many=True, allow_null=True)
    owner = UserFullSerializer(many=False, read_only=True)
    total_donations = serializers.ReadOnlyField()
    payments = PaymentForTerminalSerializer(many=True, read_only=True)
    avg_donation = serializers.ReadOnlyField()
    avg_timesession = serializers.ReadOnlyField()
    avg_gametimesession = serializers.ReadOnlyField()



# Serializer pour le model Payment
class PaymentFullSerializer(serializers.ModelSerializer):
    donator = DonatorSerializer(many=False, read_only=True)
    campaign = CampaignSerializer(many=False, read_only=True)
    terminal = TerminalSerializer(many=False, read_only=True)
    game = GameSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


# Serializer pour le model Session
# On surcharge la méthode "Create" pour calculer les timesessions
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

    def create(self, validated_data):
        if validated_data['end_time'] and validated_data['start_time'] and validated_data['end_global'] and validated_data['start_global']:
            validated_data['timesession'] = validated_data['end_time'] - validated_data['start_time']
            validated_data['timesession_global'] = validated_data['end_global'] - validated_data['start_global']
        else:
            validated_data['timesession'] = None
            validated_data['timesession_global'] = None
        session = Session.objects.create(**validated_data)
        session.save()
        return session

    def update(self, instance, validated_data):
        if validated_data['end_time'] and validated_data['start_time'] and validated_data['end_global'] and validated_data['start_global']:
            validated_data['timesession'] = validated_data['end_time'] - validated_data['start_time']
            validated_data['timesession_global'] = validated_data['end_global'] - validated_data['start_global']
        else:
            validated_data['timesession'] = None
            validated_data['timesession_global'] = None
        instance = super().update(instance, validated_data)
        return instance
