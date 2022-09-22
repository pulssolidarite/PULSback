from django.db import models
from django.conf import settings


class ScreensaverMedia(models.Model):

    PUBLIC_SCOPE = "public"
    PRIVATE_SCOPE = "private"

    SCOPE_CHOICES = (
        (PUBLIC_SCOPE, "Publique"),
        (PRIVATE_SCOPE, "Privée"),
    )

    title = models.CharField(max_length=255)

    scope = models.CharField(max_length=7, choices=SCOPE_CHOICES, default=PRIVATE_SCOPE, help_text="Public : Tous les clients ont accès à ce média. Privée : Seuls les clients visés par une diffusion de ce média chez eux ont accès à ce média.")

    # Only the owner can edit or delete this media. The owner might me an admin or a customer
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_screensave_medias", verbose_name="Propriétaire", help_text="Seul le propriétaire de ce média peut l'éditer ou le supprimer", on_delete=models.CASCADE)

    youtube_video_id = models.CharField(max_length=255, verbose_name="Id de la vidéo youtube")

    class Meta:
        verbose_name = "Média d'écran de veille"
        verbose_name_plural = "Médias d'écran de veille"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Just a little validation
        """
        assert self.scope == self.PRIVATE_SCOPE or (self.scope == self.PUBLIC_SCOPE and self.owner.is_admin_type()), "Public medias can only be owned by admin user"
        
        super(ScreensaverMedia, self).save(*args, **kwargs)    

