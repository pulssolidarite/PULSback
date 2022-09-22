from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import Avg, Sum
import datetime


class Customer(AbstractUser):
    company = models.CharField(max_length=255)
    representative = models.CharField(max_length=255, null=True)
    logo = models.FileField(blank=True, null=True, upload_to="customers/logos/")
    sales_type = models.CharField(max_length=1, default="A", null=True)
    is_archived = models.BooleanField(default=False)


    #### Herited from AbstractUser
    

    is_staff = False # Customer user cannot be staff
    is_superuser = False # Customer user cannot be superuser
    first_name = None
    last_name = None
    email = None

    # username
    # password
    # last_login
    # is_active
    # date_joined

    # We need to redefine groups field and give a different related_name so it does not clashes with the Terminal.groups related name
    groups = models.ManyToManyField(
        Group,
        verbose_name='Groups de permissions',
        blank=True,
        help_text=
            "The groups this customer belongs to. A customer will get all permissions "
            "granted to each of their groups.",
        related_name="customer_set",
        related_query_name="customer",
    )

    # We need to redefine user_permissions field and give a different related_name so it does not clashes with the Terminal.user_permissions related name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="Permissions d'utilisateur",
        blank=True,
        help_text='Specific permissions for this customer.',
        related_name="customer_set",
        related_query_name="customer",
    )

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

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
    logo = models.FileField(null=True, blank=True, upload_to="campaigns/logos/")
    squared_image = models.FileField(blank=True, null=True, upload_to="campaigns/squared_images/")
    cover = models.FileField(blank=True, null=True, upload_to="campaigns/covers/")
    description = models.TextField()
    goal_amount = models.IntegerField()
    is_video = models.BooleanField(default=True)
    video = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255)
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
    amount = models.IntegerField(blank=True)
    image = models.FileField(null=True, blank=True, upload_to="campaigns/actions/")
    text = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.PROTECT, related_name="donationSteps", null=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['amount']