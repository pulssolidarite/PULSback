from django.db import models
from django.db.models import Avg, Sum
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from game.models import Game
from fleet.models import Campaign, Customer
from backend.common import DONATION_FORMULAS

from .payment import Payment
from .session import Session


class Terminal(models.Model):
    name = models.CharField(max_length=255)

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="terminal"
    )  # User to authenticate terminal TODO rename into user
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="terminals"
    )  # Customer who own this terminal

    campaigns = models.ManyToManyField(Campaign, related_name="terminals")
    games = models.ManyToManyField(Game, related_name="terminals")
    location = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_on = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    version = models.CharField(max_length=10, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    check_for_updates = models.BooleanField(default=False)
    play_timer = models.BigIntegerField(default=10)
    free_mode_text = models.CharField(max_length=250, blank=True, null=True)
    payment_terminal = models.CharField(max_length=250, null=True, blank=True)
    donation_min_amount = models.IntegerField(default=1)
    donation_default_amount = models.IntegerField(default=1)
    donation_max_amount = models.IntegerField(default=50)
    donation_formula = models.CharField(
        max_length=250, null=True, choices=DONATION_FORMULAS
    )  # TODO set non nullable
    donation_share = models.IntegerField(
        default=50,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(0),
        ],
    )  # How much per cent of the donation go to the owner of the terminal (only if donation_formula == 'Partage')

    @property
    def visible_screensaver_broadcasts(self):
        return self.screensaver_broadcasts.filter(visible=True)

    @property
    def subscription_type(self):
        return self.customer.sales_type or None

    @property
    def total_donations(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").aggregate(
            Sum("amount")
        )["amount__sum"]

    @property
    def last_donations(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").order_by(
            "date"
        )[:5]

    @property
    def avg_donation(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").aggregate(
            Avg("amount")
        )["amount__avg"]

    @property
    def avg_timesession(self):
        avg_ts = Session.objects.filter(terminal=self.pk).aggregate(
            Avg("timesession_global")
        )["timesession_global__avg"]
        ts_string = ""
        if avg_ts:
            avg_ts = avg_ts.seconds
            hours, remainder = divmod(avg_ts, 3600)
            minutes, seconds = divmod(remainder, 60)
            ts_string = "{:02}:{:02}:{:02}".format(
                int(hours), int(minutes), int(seconds)
            )
        return ts_string

    @property
    def avg_gametimesession(self):
        avg_game_ts = Session.objects.filter(terminal=self.pk).aggregate(
            Avg("timesession")
        )["timesession__avg"]
        ts_game_string = ""
        if avg_game_ts:
            avg_game_ts = avg_game_ts.seconds
            hours, remainder = divmod(avg_game_ts, 3600)
            minutes, seconds = divmod(remainder, 60)
            ts_game_string = "{:02}:{:02}:{:02}".format(
                int(hours), int(minutes), int(seconds)
            )
        return ts_game_string

    def __str__(self):
        return "Terminal {} : {}".format(
            self.pk, "Active" if self.is_active else "False"
        )
