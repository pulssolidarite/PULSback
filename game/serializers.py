import datetime
from rest_framework import serializers
from .models import *


# Serializer pour le model Core
class CoreFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreFile
        fields = '__all__'

class BiosFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiosFile
        fields = '__all__'

class CoreSerializer(serializers.ModelSerializer):
    file = CoreFileSerializer(many=False, read_only=True)
    bios = BiosFileSerializer(many=False, read_only=True)
    nb_games = serializers.ReadOnlyField()

    class Meta:
        model = Core
        fields = '__all__'

class CoreLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Core
        fields = '__all__'


# Serializer pour le model Game
class GameFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreFile
        fields = '__all__'

class GameLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    core = CoreSerializer(many=False, read_only=True)
    file = GameFileSerializer(many=False, read_only=True)
    file2 = GameFileSerializer(many=False, read_only=True)
    nb_terminals = serializers.ReadOnlyField()

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