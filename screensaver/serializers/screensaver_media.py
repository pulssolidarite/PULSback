from rest_framework import serializers
from fleet.models import User

from screensaver.models import ScreensaverMedia


class ScreenSaverMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScreensaverMedia
        fields = ("title", "scope", "youtube_video_id", )


    def create(self, validated_data):
        user: User = self.context['request.user']

        assert user.is_staff or user.is_customer_user()

        return ScreensaverMedia(**validated_data, owner=user)