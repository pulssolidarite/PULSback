from rest_framework import serializers

from screensaver.models import ScreensaverMedia


class ScreenSaverMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScreensaverMedia
        fields = '__all__'