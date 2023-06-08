from rest_framework import serializers

from .models import *


# Serializer pour le model Core
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


# Serializer pour le model Game
class _GameFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreFile
        fields = "__all__"


class GameSerializer(serializers.ModelSerializer):
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
