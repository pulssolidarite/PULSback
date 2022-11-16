from rest_framework import serializers

from screensaver.models import ScreensaverBroadcast, ScreensaverMedia
from terminal.models import Terminal



class ScreenSaverBroadcastSerializer(serializers.ModelSerializer):
    """
    Serializer for broadcast

    Will serialize like :
        {
            visible: True,
            terminal: {
                id: 0,
                name: 'Nom du terminal',
            },
            media: {
                id: 0,
                title: 'Titre du media',
                youtube_video_id: 'ABCDEF',
            },
        }

    But will deserialize data like :
        {
            visible: True,
            terminal_id: 0, // pk of the terminal to assign to this broadcast
            media_id: 0, // pk of the media to assign to this broadcast
        }
    
    """

    class _TerminalSerializer(serializers.ModelSerializer):
        class Meta:
            model = Terminal
            fields = ('id', 'name',)

    class _MediaSerializer(serializers.ModelSerializer):
        class Meta:
            model = ScreensaverMedia
            fields = ('id', 'title', 'youtube_video_id',)

    terminal = _TerminalSerializer(read_only=True)
    terminal_id = serializers.PrimaryKeyRelatedField(source="terminal", queryset=Terminal.objects.all(), write_only=True)
    
    media = _MediaSerializer(read_only=True)
    media_id = serializers.PrimaryKeyRelatedField(source="media", queryset=ScreensaverMedia.objects.all(), write_only=True)
    
    class Meta:
        model = ScreensaverBroadcast
        fields = '__all__'