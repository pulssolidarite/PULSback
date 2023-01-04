from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from game.models import Game
from fleet.models import Campaign

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
    currency = models.CharField(max_length=255)
    payment_terminal = models.CharField(
        max_length=250, null=True
    )  # TODO add choices and set non nullable
    donation_formula = models.CharField(
        max_length=250, null=True
    )  # Classique, Gratuit, Mécénat, Partage # TODO add choices and set non nullable
    donation_share = models.IntegerField(
        default=50,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(0),
        ],
    )  # How much per cent of the donation go to the owner of the terminal (only if donation_formula == 'Partage')

    # Save terminal donation formula and payment terminal in payment
    # In case the terminal donation formula or the payment terminal change in the futur,
    # we keep track of the donation formula and the payment terminal at the time of the payment
    donation_formula = models.CharField(
        max_length=250, null=True, blank=True
    )  # TODO can be null ?
    payment_terminal = models.CharField(
        max_length=250, null=True, blank=True
    )  # TODO can be null ?

    def __str__(self):
        return "Payment of {} {} by {}".format(self.amount, self.currency, self.donator)

    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.donation_formula:
                self.donation_formula = self.terminal.donation_formula

            if not self.payment_terminal:
                self.payment_terminal = self.terminal.payment_terminal

        super(Payment, self).save(*args, **kwargs)

    @property
    def amount_donated(self) -> float:
        if self.donation_formula == "Partage":
            return self.amount * float(self.donation_share) / 100

        else:
            return self.amount
