from django.db import models

from game.models import Game
from fleet.models import Campaign

from backend.common import DONATION_FORMULAS

from .donator import Donator


class Payment(models.Model):
    donator = models.ForeignKey(
        Donator,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Donateur",
    )  # Can be null if the paiment was skipped

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Campagne",
    )

    terminal = models.ForeignKey(
        "terminal.Terminal",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Borne",
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        null=True,
        related_name="payments",
        verbose_name="Jeu",
    )

    date = models.DateTimeField(auto_now=True)

    method = models.CharField(
        max_length=255, verbose_name="Méthode de paiement"
    )  # TODO add choices and set non nullable

    status = models.CharField(
        max_length=255, verbose_name="Status du paiement"
    )  # TODO add choices and set non nullable

    amount = models.FloatField(verbose_name="Montant du paiement")

    amount_donated = models.FloatField(
        null=True, verbose_name="Montant reversé pour la campagne"
    )

    currency = models.CharField(max_length=255, verbose_name="Monnaie")

    payment_terminal = models.CharField(
        max_length=250, null=True, verbose_name="TPE"
    )  # TODO add choices and set non nullable

    donation_formula = models.CharField(
        max_length=250,
        null=True,
        choices=DONATION_FORMULAS,
        verbose_name="Formule de don",
    )  # TODO add choices and set non nullable

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-date"]

    def __str__(self):
        return "Paiement de {} {} le {}".format(self.amount, self.currency, self.date)

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

    def get_amount_donated_for_old_payments(self):
        # TODO assign to each paiment its amount donated and donation formula then remove this shit
        if self.amount_donated:
            return self.amount_donated

        donation_formula = (
            self.donation_formula
            if self.donation_formula
            else self.terminal.donation_formula
        )

        if donation_formula == "Partage":
            return self.amount * float(self.terminal.donation_share) / 100

        else:
            return self.amount
