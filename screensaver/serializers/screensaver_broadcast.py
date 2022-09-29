from rest_framework import serializers

from screensaver.models import ScreensaverBroadcast, ScreensaverMedia
from terminal.models import Terminal



class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = ('id', 'name',)

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreensaverMedia
        fields = ('id', 'title',)

class ScreenSaverBroadcastReadSerializer(serializers.ModelSerializer):
    """
    This serializer is to be used for serialize broadcast, including terminal and media info.
    """
    terminal = TerminalSerializer(read_only=True)
    media = MediaSerializer(read_only=True)

    class Meta:
        model = ScreensaverBroadcast
        fields = '__all__'


class ScreenSaverBroadcastWriteSerializer(serializers.ModelSerializer):
    """
    This serializer is to be used for deserialize broadcast.
    To assign terminal or media, include :
    {
        terminal: pk of the terminal,
        media : pk of the media,
    }
    """

    class Meta:
        model = ScreensaverBroadcast
        fields = '__all__'