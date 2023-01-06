from rest_framework import serializers
from fleet.models import User

from screensaver.models import ScreensaverMedia


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize User but only contact info, no sensitive info
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class ScreenSaverMediaSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    nb_terminals = serializers.ReadOnlyField()  # Property on model ScreensaverMedia

    class Meta:
        model = ScreensaverMedia
        fields = (
            "id",
            "title",
            "scope",
            "owner",
            "vimeo_video_id",
            "nb_terminals",
        )

    def create(self, validated_data):
        user: User = self.context["request"].user

        assert user.is_staff or user.is_customer_user()

        screensaver_media = ScreensaverMedia(**validated_data, owner=user)

        screensaver_media.save()

        return screensaver_media
