from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.decorators import action

from fleet.models import User, Campaign, Customer
from fleet.serializers import CampaignSerializer

from backend.permissions import IsAdminOrCustomerUser

from terminal.models import Terminal

from terminal.serializers import (
    FullTerminalSerializer,
)

from game.models import Game


class _GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class _CampaignSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ("name",)


class _CustomerSerializerCompanyOnly(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("company",)


class _TerminalSerializerForListing(serializers.ModelSerializer):
    campaigns = _CampaignSerializerNameOnly(many=True, read_only=True)
    customer = _CustomerSerializerCompanyOnly(read_only=True)

    class Meta:
        model = Terminal
        fields = (
            "id",
            "name",
            "is_active",
            "is_on",
            "is_playing",
            "campaigns",
            "customer",
            "version",
            "total_donations",
        )


class TerminalViewSet(viewsets.ModelViewSet):
    """
    This view is used from SETH front admin or customer
    """

    queryset = Terminal.objects.filter(is_archived=False)
    serializer_class = FullTerminalSerializer

    def get_queryset(self):
        user: User = self.request.user

        if user.is_customer_user():
            return Terminal.objects.filter(
                is_archived=False, customer=user.get_customer()
            )  # For customer, return all terminals that belong to this customer

        elif user.is_staff:
            return Terminal.objects.filter(is_archived=False)

        else:
            raise PermissionDenied()

    def get_permissions(self):
        """
        Allow admin and customers to list, retrieve and update but only admin to do any other actions

        """
        if (
            self.action == "list"
            or self.action == "retrieve"
            or self.action == "update"
        ):
            permission_classes = [IsAuthenticated, IsAdminOrCustomerUser]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def list(self, request):
        is_active = request.query_params.get("is_active", None)
        is_on = request.query_params.get("is_on", None)
        is_playing = request.query_params.get("is_playing", None)
        customer_id = request.query_params.get("customer_id", None)

        queryset = self.get_queryset()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == "true")

        if is_on is not None:
            queryset = queryset.filter(is_on=is_on == "true")

        if is_playing is not None:
            queryset = queryset.filter(is_playing=is_playing == "true")

        if customer_id is not None:
            queryset = queryset.filter(customer_id=customer_id)

        serializer = _TerminalSerializerForListing(queryset, many=True, read_only=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def activate(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.is_active = True
        terminal.owner.is_active = True
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"])
    def deactivate(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.is_active = False
        terminal.owner.is_active = False
        terminal.is_on = False
        terminal.is_playing = False
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get", "post"])
    def archive(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.is_active = False
        terminal.owner.is_active = False
        terminal.is_archived = True
        terminal.save()
        terminal.owner.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def check_for_updates(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        terminal.check_for_updates = True
        terminal.save()
        serializer = FullTerminalSerializer(terminal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def campaigns(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        campaigns = terminal.campains
        serializer = CampaignSerializer(
            campaigns, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def games(self, request, pk, format=None):
        terminal: Terminal = get_object_or_404(self.get_queryset(), pk=pk)
        games = terminal.games
        games = _GameSerializer(games, many=True, context={"request": request})
        return Response(games.data, status=status.HTTP_200_OK)
