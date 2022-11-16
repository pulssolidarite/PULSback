from django.db import models

from terminal.models import Terminal

from .screensaver_media import ScreensaverMedia



class ScreensaverBroadcast(models.Model):

    terminal = models.ForeignKey(Terminal, verbose_name="Terminal", on_delete=models.CASCADE, related_name="screensaver_broadcasts")
    media = models.ForeignKey(ScreensaverMedia, verbose_name="Média", on_delete=models.CASCADE, related_name="screensaver_broadcasts")

    visible = models.BooleanField(verbose_name="Visible", default=False)

    class Meta:
        verbose_name = "Diffusion d'écran de veille"
        verbose_name_plural = "Diffusions d'écran de veille"

    def __str__(self):
        return f"Diffusion de {self.media} chez {self.terminal.customer}"