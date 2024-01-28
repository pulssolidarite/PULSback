import datetime

import pytz
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Sum
from django.utils import timezone

from backend.common import DONATION_FORMULAS
from fleet.models import Campaign, Customer
from game.models import Game

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
    play_timer = models.BigIntegerField(default=10)  # Time (in minutes)
    free_mode_text = models.CharField(max_length=250, blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=False)
    is_on = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    version = models.CharField(max_length=10, null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    # Commands
    check_for_updates = models.BooleanField(default=False)
    restart = models.BooleanField(
        default=False, verbose_name="Dire à la borne de redémarrer une fois"
    )
    restart_every_day_from = models.TimeField(
        null=True, blank=True, verbose_name="Redémarrer tous les jours à partir de"
    )
    restart_every_day_until = models.TimeField(
        null=True, blank=True, verbose_name="Redémarrer tous les jours jusqu'à"
    )
    last_restarted = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="La borne a redémarré pour la dernière fois le",
        editable=False,
    )

    # Payment terminal

    payment_terminal = models.CharField(max_length=250, null=True, blank=True)

    PAYTER = "PAYTER"
    PAX = "PAX"

    PAYMENT_TERMINAL_TYPE_CHOICES = (
        (PAYTER, PAYTER),
        (PAX, PAX),
    )

    payment_terminal_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TERMINAL_TYPE_CHOICES,
        default=PAYTER,
        verbose_name="Type de terminal de paiement",
    )

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

    class Meta:
        verbose_name = "Borne"
        verbose_name_plural = "Bornes"

    def __str__(self):
        return "Terminal {} : {}".format(
            self.pk, "Active" if self.is_active else "False"
        )

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

    @property
    def should_restart(self):
        def is_datetime_between_times(
            _datetime: datetime.datetime,
            start_time: datetime.time,
            end_time: datetime.time,
        ):
            start_datetime = datetime.datetime.combine(
                datetime.date.today(), start_time
            )

            end_datetime = datetime.datetime.combine(datetime.date.today(), end_time)

            if start_datetime <= _datetime <= end_datetime:
                return True

            elif start_datetime > end_datetime:
                if _datetime.date() == datetime.date.today() and (
                    _datetime.time() >= start_datetime.time()
                    or _datetime.time() <= end_datetime.time()
                ):
                    return True

        if self.restart:
            return True

        if self.restart_every_day_from and self.restart_every_day_until:
            if is_datetime_between_times(
                datetime.datetime.now(),
                self.restart_every_day_from,
                self.restart_every_day_until,
            ):
                if self.last_restarted is None:
                    return True

                return not is_datetime_between_times(
                    self.last_restarted,
                    self.restart_every_day_from,
                    self.restart_every_day_until,
                )

        return False
