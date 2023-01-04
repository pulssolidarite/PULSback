from django.db import models

from game.models import Game
from fleet.models import Campaign

from backend.common import DONATION_FORMULAS

from .donator import Donator


class Payment(models.Model):
    donator = models.ForeignKey(
        Donator, on_delete=models.PROTECT, null=True, related_name="payments"
    )
    campaign = models.ForeignKey(
        Campaign, on_delete=models.PROTECT, related_name="payments"
    )
    terminal = models.ForeignKey(
        "terminal.Terminal", on_delete=models.PROTECT, related_name="payments"
    )
    game = models.ForeignKey(
        Game, on_delete=models.PROTECT, null=True, related_name="payments"
    )
    date = models.DateTimeField(auto_now=True)
    method = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    amount = models.FloatField()
    amount_donated = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=255)

    payment_terminal = models.CharField(
        max_length=250, null=True, blank=True
    )  # TODO add choices and set non nullable

    donation_formula = models.CharField(
        max_length=250, null=True, blank=True, choices=DONATION_FORMULAS
    )  # TODO add choices and set non nullable

    def __str__(self):
        return "Payment of {} {} by {}".format(self.amount, self.currency, self.donator)

    def save(self, *args, **kwargs):
        if not self.pk:

            # Payment is being created

            if not self.payment_terminal:
                self.payment_terminal = self.terminal.payment_terminal

            if not self.donation_formula:
                self.donation_formula = self.terminal.donation_formula

            if not self.amount_donated:
                if self.donation_formula == "Partage":
                    self.amount_donated = (
                        self.amount * float(self.terminal.donation_share) / 100
                    )
                else:
                    self.amount_donated = self.amount

        super(Payment, self).save(*args, **kwargs)
