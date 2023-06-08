from rest_framework import serializers
from .models import Game


# Serializer pour le model Core


class GameSerializer(serializers.ModelSerializer):
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
