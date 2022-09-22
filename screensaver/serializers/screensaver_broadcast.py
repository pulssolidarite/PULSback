from rest_framework import serializers

from screensaver.models import ScreensaverBroadcast


class ScreenSaverBroadcastSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScreensaverBroadcast
        fields = '__all__'