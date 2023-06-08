from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveDestroyAPIView,
    UpdateAPIView,
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets

from django.shortcuts import get_object_or_404

from .forms import *

from fleet.models import User
from backend.permissions import IsAdminOrCustomerUser, NonAdminUserCanOnlyGet

from .models import Core, Game


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


class _CoreLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = "__all__"


class _ExtendedGameSerializer(serializers.ModelSerializer):
    core = _CoreSerializer(many=False, read_only=True)
    file = _GameFileSerializer(many=False, read_only=True)
    nb_terminals = serializers.ReadOnlyField()

    core_id = serializers.PrimaryKeyRelatedField(
        queryset=Core.objects.all(), source="core", write_only=True, required=False
    )

    file_id = serializers.PrimaryKeyRelatedField(
        queryset=GameFile.objects.all(), source="file", write_only=True
    )

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


class _GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    permission_classes = [
        IsAuthenticated,
        IsAdminOrCustomerUser,
        NonAdminUserCanOnlyGet,
    ]

    def get_serializer_class(self):
        user: User = self.request.user

        if user.is_staff:
            return _ExtendedGameSerializer  # Return extended serializer only for admin

        return _GameSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_queryset().filter(is_archived=False).order_by("-featured", "name"),
            many=True,
            read_only=True,
        )
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        game = get_object_or_404(self.get_queryset(), pk=pk)
        game.is_archived = True
        game.terminals.clear()
        game.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def upload(self, request):
        if not request.FILES["file"]:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        form = GameFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            return Response(
                _GameFileSerializer(file).data, status=status.HTTP_201_CREATED
            )
        else:
            print(form.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminOrCustomerUser],
    )
    def toggle_featured(self, request, pk, format=None):
        user: User = request.user
        game = get_object_or_404(self.get_queryset(), pk=pk)

        if user.is_staff:
            game.featured = not game.featured
            game.save()

        else:
            customer = user.get_customer()
            if customer.featured_game == game:
                customer.featured_game = None
            else:
                customer.featured_game = game
            customer.save()

        return Response(status=status.HTTP_200_OK)


# Core Model
class CoreListView(ListAPIView):
    serializer_class = _CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin


class CoreCreateView(CreateAPIView):
    serializer_class = _CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin


class CoreRetrieveDestroyView(RetrieveDestroyAPIView):
    serializer_class = _CoreSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin


class CoreUpdateView(UpdateAPIView):
    serializer_class = _CoreLightSerializer
    queryset = Core.objects.filter()
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin


class CoreFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin

    def post(self, request, format=None):
        if request.FILES["file"]:
            form = CoreFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(
                    _CoreFileSerializer(file).data, status=status.HTTP_201_CREATED
                )
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)


class BiosFileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admin

    def post(self, request, format=None):
        if request.FILES["file"]:
            form = BiosFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save()
                return Response(
                    _BiosFileSerializer(file).data, status=status.HTTP_201_CREATED
                )
            else:
                print(form.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)
