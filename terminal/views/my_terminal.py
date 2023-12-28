from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework import status, serializers

from fleet.models import Customer
from fleet.serializers import CampaignSerializer

from backend.permissions import TerminalIsAuthenticated

from terminal.models import Terminal

from game.models import CoreFile, BiosFile, Core, Game

from screensaver.serializers.screensaver_broadcast import ScreenSaverBroadcastSerializer


class _CoreFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreFile
        fields = "__all__"


class _BiosFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiosFile
        fields = "__all__"


class _CoreSerializer(serializers.ModelSerializer):
    file = _CoreFileSerializer(many=False, read_only=True)
    bios = _BiosFileSerializer(many=False, read_only=True)
    nb_games = serializers.ReadOnlyField()

    class Meta:
        model = Core
        fields = "__all__"


class _GameFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreFile
        fields = "__all__"


class _GameSerializer(serializers.ModelSerializer):
    core = _CoreSerializer(many=False, read_only=True)
    file = _GameFileSerializer(many=False, read_only=True)

    class Meta:
        model = Game
        fields = "__all__"


class LightTerminalSerializer(serializers.ModelSerializer):
    """
    This serialize ONLY STRICTLY NECESSARY DATA FOR HERA.
    It should serialize only public data as it will be sent to Hera, NO SENSIBLE DATA !
    (for example, only visible screensavers, not all of them)
    """

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
            games_serializer = _GameSerializer(
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
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

    @action(detail=False, methods=["post"])
    def turn_on(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_on:
                terminal.is_on = True
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

    @action(detail=False, methods=["post"])
    def is_running(self, request):
        try:
            terminal: Terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_on:
                terminal.is_on = True

            terminal.version = request.data.get("version")

            check_for_updates_required = terminal.check_for_updates
            terminal.check_for_updates = False

            terminal.save()

            return Response(
                {
                    "check_for_updates": check_for_updates_required,
                }
            )

        except ObjectDoesNotExist:
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

    @action(detail=False, methods=["post"])
    def start_playing(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if not terminal.is_playing:
                terminal.is_playing = True
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

    @action(detail=False, methods=["post"])
    def stop_playing(self, request):
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            if terminal.is_playing:
                terminal.is_playing = False
                terminal.save()

            return Response()

        except ObjectDoesNotExist:
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

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
            status = status.HTTP_404_NOT_FOUND, data = {"error": "Terminal not found"}

    @action(detail=False, methods=["post"])
    def restart(self, request):
        """
        Endpoint to restart terminak
        """
        try:
            terminal = Terminal.objects.get(owner=request.user.id)
            terminal.restart = True
            terminal.save()

            return Response()

        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "Terminal not found"}
            )

    @action(detail=False, methods=["get"])
    def commands(self, request):
        """
        Endpoint to retrieve commands to execute on terminal
        """
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            commands = []

            if terminal.restart:
                commands.append("sudo reboot")
                terminal.restart = False
                terminal.save()

            return Response({"commands": commands})

        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "Terminal not found"}
            )

    @action(detail=False, methods=["post"])
    def hera_flask_logs(self, request):
        """
        Endpoint to save logs from Hera Flask
        """
        try:
            terminal = Terminal.objects.get(owner=request.user.id)

            return Response()

        except ObjectDoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"error": "Terminal not found"}
            )
