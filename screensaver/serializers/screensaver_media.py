from rest_framework import serializers
from fleet.models import User

from screensaver.models import ScreensaverMedia

from fleet.serializers import UserSerializer


class ScreenSaverMediaSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = ScreensaverMedia
        fields = ("title", "scope", "youtube_video_id", "owner", )


    def create(self, validated_data):
        user: User =  self.context['request'].user

        assert user.is_staff or user.is_customer_user()

        screensaver_media = ScreensaverMedia(**validated_data, owner=user)

        screensaver_media.save()

        return screensaver_media