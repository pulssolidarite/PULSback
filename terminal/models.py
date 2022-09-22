from django.db import models
from django.conf import settings
from fleet.models import Campaign
from django.db.models import Avg, Sum
from game.models import Game
from django.contrib.auth.models import AbstractUser, Group, Permission


class Terminal(AbstractUser):
    name = models.CharField(max_length=255)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="terminal")
    campaigns = models.ManyToManyField(Campaign, related_name="terminals")
    games = models.ManyToManyField(Game, related_name="terminals")
    location = models.CharField(max_length=255, null=True, blank=True)
    is_on = models.BooleanField(default=False)
    is_playing = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    play_timer = models.BigIntegerField(default=10)
    free_mode_text = models.CharField(max_length=250, blank=True, null=True)
    payment_terminal = models.CharField(max_length=250, null=True, blank=True)
    donation_formula = models.CharField(max_length=250, null=True)


    #### Herited from AbstractUser
    

    is_staff = False # Terminal user cannot be staff
    is_superuser = False # Terminal user cannot be superuser
    first_name = None
    last_name = None
    email = None
    is_active = models.BooleanField(default=False) # Change field default value to False

    # username
    # password
    # last_login
    # date_joined

    # We need to redefine groups field and give a different related_name so it does not clashes with the Customer.groups related name
    groups = models.ManyToManyField(
        Group,
        verbose_name='Groups de permissions',
        blank=True,
        help_text=
            "The groups this terminal belongs to. A terminal will get all permissions "
            "granted to each of their groups.",
        related_name="terminal_set",
        related_query_name="terminal",
    )

    # We need to redefine user_permissions field and give a different related_name so it does not clashes with the Customer.user_permissions related name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="Permissions d'utilisateur",
        blank=True,
        help_text='Specific permissions for this terminal.',
        related_name="terminal_set",
        related_query_name="terminal",
    )

    class Meta:
        verbose_name = 'Terminal'
        verbose_name_plural = 'Terminaux'


    @property
    def subscription_type(self):
        if self.owner.customer:
            return self.owner.customer.sales_type or None

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

    def __str__(self):
        return "Payment of {} {} by {}".format(self.amount, self.currency, self.donator)