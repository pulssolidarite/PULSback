from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, Sum
import datetime


class Customer(models.Model):
    company = models.CharField(max_length=255)
    representative = models.CharField(max_length=255, null=True)
    sales_type = models.CharField(max_length=1, default="A", null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.company or ""


class User(AbstractUser):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="users", null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Campaign(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name="campaigns")
    name = models.CharField(max_length=255)
    description = models.TextField()
    # photo1 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text1 = models.TextField(null=True, blank=True)
    # photo5 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text5 = models.TextField(null=True, blank=True)
    # photo10 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text10 = models.TextField(null=True, blank=True)
    # photo20 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text20 = models.TextField(null=True, blank=True)
    # photo30 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text30 = models.TextField(null=True, blank=True)
    # photo50 = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    # text50 = models.TextField(null=True, blank=True)
    goal_amount = models.IntegerField()
    is_video = models.BooleanField(default=True)
    video = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255)
    logo = models.FileField(null=True, blank=True, upload_to="campaigns/logos/")
    is_archived = models.BooleanField(default=False)

    @property
    def nb_terminals(self):
        return self.terminals.count()

    @property
    def avg_donation(self):
        return self.payments.filter(campaign=self.pk, status="Accepted").aggregate(Avg('amount'))['amount__avg']

    @property
    def total_today(self):
        return self.payments.filter(campaign=self.pk, status="Accepted", date=datetime.datetime.today()).aggregate(Sum('amount'))['amount__sum']

    @property
    def total_ever(self):
        return self.payments.filter(campaign=self.pk, status="Accepted").aggregate(Sum('amount'))['amount__sum']

    @property
    def last_donations(self):
        return self.payments.filter(campaign=self.pk, status="Accepted").order_by('date')

    def __str__(self):
        return self.name

class DonationStep(models.Model):
    amount = models.IntegerField()
    # photo = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    text = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="donationSteps", null=True)

    def __str__(self):
        return self.text
