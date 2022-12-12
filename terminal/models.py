from django.db import models
from django.db.models import Avg, Sum
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from game.models import Game
from fleet.models import Campaign, Customer


class Terminal(models.Model):
    name = models.CharField(max_length=255)

    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="terminal") # User to authenticate terminal TODO rename into user
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="terminals") # Customer who own this terminal

    campaigns = models.ManyToManyField(Campaign, related_name="terminals")
    games = models.ManyToManyField(Game, related_name="terminals")
    location = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_on = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    play_timer = models.BigIntegerField(default=10)
    free_mode_text = models.CharField(max_length=250, blank=True, null=True)
    payment_terminal = models.CharField(max_length=250, null=True, blank=True)
    donation_min_amount = models.IntegerField(default=1)
    donation_default_amount = models.IntegerField(default=1)
    donation_max_amount = models.IntegerField(default=50)
    donation_formula = models.CharField(max_length=250, null=True) # Classique, Gratuit, Mécénat, Partage
    donation_share = models.IntegerField(default=50) # How much per cent of the donation go to the owner of the terminal (only if donation_formula == 'Partage')


    @property
    def visible_screensaver_broadcasts(self):
        return self.screensaver_broadcasts.filter(visible=True)

    @property
    def subscription_type(self):
        return self.customer.sales_type or None

    @property
    def total_donations(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").aggregate(Sum('amount'))['amount__sum']

    @property
    def last_donations(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").order_by('date')[:5]

    @property
    def avg_donation(self):
        return Payment.objects.filter(terminal=self.pk, status="Accepted").aggregate(Avg('amount'))['amount__avg']

    @property
    def avg_timesession(self):
        avg_ts = Session.objects.filter(terminal=self.pk).aggregate(Avg('timesession_global'))['timesession_global__avg']
        ts_string = ''
        if avg_ts:
            avg_ts = avg_ts.seconds
            hours, remainder = divmod(avg_ts, 3600)
            minutes, seconds = divmod(remainder, 60)
            ts_string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        return ts_string

    @property
    def avg_gametimesession(self):
        avg_game_ts = Session.objects.filter(terminal=self.pk).aggregate(Avg('timesession'))['timesession__avg']
        ts_game_string = ''
        if avg_game_ts:
            avg_game_ts = avg_game_ts.seconds
            hours, remainder = divmod(avg_game_ts, 3600)
            minutes, seconds = divmod(remainder, 60)
            ts_game_string = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        return ts_game_string

    def __str__(self):
        return 'Terminal {} : {}'.format(self.pk, 'Active' if self.is_active else 'False')


class Donator(models.Model):
    email = models.EmailField(blank=True, null=True)
    accept_asso = models.BooleanField(blank=True, null=True, default=False)
    accept_newsletter = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        if self.email:
            return self.email
        return 'Donator {}'.format(self.pk)


class Session(models.Model):
    donator = models.ForeignKey(Donator, on_delete=models.PROTECT, related_name="sessions")
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="sessions")
    terminal = models.ForeignKey(Terminal, on_delete=models.PROTECT, related_name="sessions")
    game = models.ForeignKey(Game, on_delete=models.PROTECT, null=True, related_name="sessions")
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    start_global = models.DateTimeField(blank=True, null=True)
    end_global = models.DateTimeField(blank=True, null=True)
    position_asso = models.IntegerField()
    timesession = models.DurationField(blank=True, null=True)
    timesession_global = models.DurationField(blank=True, null=True)

    def __str__(self):
        return "Session {} : {} global".format(self.pk, self.timesession_global)


class Payment(models.Model):
    donator = models.ForeignKey(Donator, on_delete=models.PROTECT, null=True, related_name="payments")
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="payments")
    terminal = models.ForeignKey(Terminal, on_delete=models.PROTECT, related_name="payments")
    game = models.ForeignKey(Game, on_delete=models.PROTECT, null=True, related_name="payments")
    date = models.DateTimeField(auto_now=True)
    method = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    amount = models.FloatField()
    currency = models.CharField(max_length=255)
    payment_terminal = models.CharField(max_length=250, null=True) # TODO add choices and set non nullable
    donation_formula = models.CharField(max_length=250, null=True) # Classique, Gratuit, Mécénat, Partage # TODO add choices and set non nullable
    donation_share = models.IntegerField(
        default=50,
        validators=[
            MaxValueValidator(50),
            MinValueValidator(0),
        ],
    ) # How much per cent of the donation go to the owner of the terminal (only if donation_formula == 'Partage')

    # Save terminal donation formula and payment terminal in payment
    # In case the terminal donation formula or the payment terminal change in the futur,
    # we keep track of the donation formula and the payment terminal at the time of the payment
    donation_formula = models.CharField(max_length=250, null=True, blank=True) # TODO can be null ? 
    payment_terminal = models.CharField(max_length=250, null=True, blank=True) # TODO can be null ? 

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
