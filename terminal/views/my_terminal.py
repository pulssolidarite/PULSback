from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework import status


from fleet.serializers import CampaignSerializer

from backend.permissions import TerminalIsAuthenticated

from terminal.models import Terminal
from terminal.serializers import *


class MyTerminalViewSet(GenericViewSet):
    permission_classes = [TerminalIsAuthenticated]

    def list(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal_serializer = LightTerminalSerializer(terminal)
            campaigns_serializer = CampaignSerializer(
                terminal.campaigns.order_by("-featured", "name"),
                many=True,
                context={"request": request},
            )
            games_serializer = GameSerializer(
                terminal.games.order_by("-featured", "name"),
                many=True,
                context={"request": request},
            )
            return Response(
                {
                    "terminal": terminal_serializer.data,
                    "campaigns": campaigns_serializer.data,
                    "games": games_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def turn_on(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_on:
                terminal.is_on = True
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def is_running(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_on:
                terminal.is_on = True
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def start_playing(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_playing:
                terminal.is_playing = True
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def stop_playing(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if terminal.is_playing:
                terminal.is_playing = False
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def turn_off(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if terminal.is_on:
                terminal.is_on = False
                terminal.is_playing = False
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
