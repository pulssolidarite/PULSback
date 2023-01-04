from django.db import models

from game.models import Game
from fleet.models import Campaign

from .donator import Donator


class Session(models.Model):
    donator = models.ForeignKey(
        Donator, on_delete=models.PROTECT, related_name="sessions"
    )
    campaign = models.ForeignKey(
        Campaign, on_delete=models.PROTECT, related_name="sessions"
    )
    terminal = models.ForeignKey(
        "terminal.Terminal", on_delete=models.PROTECT, related_name="sessions"
    )
    game = models.ForeignKey(
        Game, on_delete=models.PROTECT, null=True, related_name="sessions"
    )
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    start_global = models.DateTimeField(blank=True, null=True)
    end_global = models.DateTimeField(blank=True, null=True)
    position_asso = models.IntegerField()
    timesession = models.DurationField(blank=True, null=True)
    timesession_global = models.DurationField(blank=True, null=True)

    def __str__(self):
        return "Session {} : {} global".format(self.pk, self.timesession_global)
