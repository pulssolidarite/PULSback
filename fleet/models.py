from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, Sum
from django.conf import settings

import datetime


class User(AbstractUser):
    """
    user can be assigned to a terminal (user.terminal != None),
    or it can be assigned to a customer (user.customer != None),
    or it can be an admin (user.is_staff == True) (note that admin users can be superusers or not),
    
    The pre save validation makes sure that a user object is an admin or is assigned to a customer or a terminal.
    """

    # Referenced my Terminal model with related name 'terminal'
    # Referenced my Customer model with related name 'customer'
    # Referenced my Campaign model with related name 'campaigns'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        Perform some pre save validations
        """

        assert not (self.get_customer() and self.get_terminal()), "User cannot be assigned to a customer and a terminal in the same time. Use different users."
        assert not (self.is_staff and self.get_terminal()), "Staff member cannot be assigned to a terminal."
        assert not (self.is_staff and self.get_customer()), "Staff member cannot be assigned to a customer."

        super(User, self).save(*args, **kwargs)

    def get_terminal(self):
        if hasattr(self, 'terminal'):
            return self.terminal

        return None

    def get_customer(self):
        if hasattr(self, 'customer'):
            return self.customer

        return None

    def is_terminal_user(self):
        return self.get_terminal() is not None

    def is_customer_user(self):
        return self.get_customer() is not None


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="customer", null=True) # TODO assign user to every customers then set this field to null=False

    company = models.CharField(max_length=255)
    representative = models.CharField(max_length=255, null=True)
    logo = models.FileField(blank=True, null=True, upload_to="customers/logos/")
    sales_type = models.CharField(max_length=1, default="A", null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    can_edit_featured_content = models.BooleanField(default=False)
    can_edit_donation_formula = models.BooleanField(default=False)
    can_edit_screensaver_broadcasts = models.BooleanField(default=False)
    can_see_donators = models.BooleanField(default=False)

    def __str__(self):
        return self.company or ""




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
    featured = models.BooleanField(verbose_name="Asso du moment", default=False)

    def save(self, *args, **kwargs):
        """
        Make sure only one Campaign object has featured == True
        """
        if self.featured:
            try:
                old_featured = Campaign.objects.get(featured=True)
                if old_featured and self != old_featured:
                    old_featured.featured = False
                    old_featured.save()
            except Campaign.DoesNotExist:
                pass
            
        super(Campaign, self).save(*args, **kwargs)

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