from rest_framework import serializers
from fleet.models import Campaign, DonationStep


class DonationStepSerializer(serializers.ModelSerializer):
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all())

    class Meta:
        model = DonationStep
        fields = "__all__"

    def get_image_url(self, step):
        if step.image:
            if self.context.get("request"):
                request = self.context.get("request")
                image_url = step.image.url
                return request.build_absolute_uri(image_url)
            else:
                return step.image.url
        else:
            return step.image
