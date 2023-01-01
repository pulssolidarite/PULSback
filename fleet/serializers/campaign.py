from rest_framework import serializers
from fleet.models import Campaign
from terminal.models import Payment, Game
from django.db.models import Sum


from .donation_step import DonationStepSerializer


class _GameForCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"

    def get_logo_url(self, game):
        if game.logo:
            if self.context.get("request"):
                request = self.context.get("request")
                logo_url = game.logo.url
                return request.build_absolute_uri(logo_url)
            else:
                return game.logo.url
        else:
            return game.logo


class _PaymentForCampaignSerializer(serializers.ModelSerializer):
    game = _GameForCampaignSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"


class CampaignFullSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    collected = serializers.SerializerMethodField("get_collected")
    nb_terminals = serializers.ReadOnlyField()
    avg_donation = serializers.ReadOnlyField()
    total_today = serializers.ReadOnlyField()
    total_ever = serializers.ReadOnlyField()
    last_donations = _PaymentForCampaignSerializer(many=True, read_only=True)
    donationSteps = DonationStepSerializer(many=True, required=False)

    class Meta:
        model = Campaign
        fields = "__all__"

    def get_logo_url(self, campaign):
        if campaign.logo:
            if self.context.get("request"):
                request = self.context.get("request")
                logo_url = campaign.logo.url
                return request.build_absolute_uri(logo_url)
            else:
                return campaign.logo.url
        else:
            return campaign.logo

    def get_collected(self, campaign):
        return (
            Payment.objects.filter(campaign=campaign.id, status="Accepted").aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )


# Serializer pour le model Campaign
class CampaignSerializer(serializers.ModelSerializer):
    donationSteps = DonationStepSerializer(many=True, required=False)

    class Meta:
        model = Campaign
        fields = "__all__"

    def get_logo_url(self, campaign):
        if campaign.logo:
            if self.context.get("request"):
                request = self.context.get("request")
                logo_url = campaign.logo.url
                return request.build_absolute_uri(logo_url)
            else:
                return campaign.logo.url
        else:
            return campaign.logo

    def get_collected(self, campaign):
        return (
            Payment.objects.filter(campaign=campaign.id, status="Accepted").aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )
