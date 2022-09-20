from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg, Sum
import datetime

class Customer(models.Model):
    login_user = models.OneToOneField("fleet.User", on_delete=models.PROTECT, related_name="login_customer", null=True)
    company = models.CharField(max_length=255)
    representative = models.CharField(max_length=255, null=True)
    logo = models.FileField(blank=True, null=True, upload_to="customers/logos/")
    sales_type = models.CharField(max_length=1, default="A", null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.company or ""


class User(AbstractUser):
    """
    TODO so it can be cleaner and easier for API permission access, we should do something like :
    Remove is_admin

    user_type = [
        Admin, # To login to Admin space (and if user has is_staff=True, it can also login to Django admin backoffice, and if user also has is_superuser = True, he got all permissions on Django admin backoffice)
        Terminal, # To login a terminal from Hera
        Customer, # To login a customer into the customer space.
    ]

    Each terminal should have OneToOne relationship with a user of type "terminal"
    Each customer should have OneToOne relationship with a user of type "customer"
    
    """

    USER_TYPE_ADMIN = "admin"
    USER_TYPE_CUSTOMER = "customer"
    USER_TYPE_TERMINAL = "terminal"

    USER_TYPE_CHOICES = (
        (USER_TYPE_ADMIN, "Administrateur"),
        (USER_TYPE_TERMINAL, "Terminal"),
        (USER_TYPE_CUSTOMER, "Client"),
    )

    user_type = models.CharField(
        verbose_name="Type d'utilisateur", max_length=8, choices=USER_TYPE_CHOICES, null=True
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="users", null=True) # This field is for terminal type user, to identify the customer who own the terminal. TODO this field should really be moved to Terminal model
    is_admin = models.BooleanField(default=False) # TODO remove and use type admin instead

    def __str__(self):
        return self.username

    def is_customer_type(self):
        return self.user_type == self.USER_TYPE_CUSTOMER

    def is_admin_type(self):
        return self.user_type == self.USER_TYPE_ADMIN or self.is_staff

    def is_terminal_type(self):
        return self.user_type == self.USER_TYPE_TERMINAL

    

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


class ScreensaverMedia(models.Model):

    PUBLIC_SCOPE = "public"
    PRIVATE_SCOPE = "private"

    SCOPE_CHOICES = (
        (PUBLIC_SCOPE, "Publique"),
        (PRIVATE_SCOPE, "Privée"),
    )

    title = models.CharField(max_length=255)

    # If scope is public, all customers will have access to this media, independently of the 'customers' field
    # If scope is private, you need to create broadcast to broadcast media to a customer
    scope = models.CharField(max_length=7, choices=SCOPE_CHOICES, default=PRIVATE_SCOPE, help_text="Public : Tous les clients ont accès à ce média. Privée : Vous devez créer des diffusions pour diffuser le média chez des clients spécifiques.")

    # Only the owner can edit or delete this media. The owner might me an admin or a customer
    owner = models.ForeignKey(User, related_name="owned_screensave_medias", verbose_name="Propriétaire", help_text="Seul le propriétaire de ce média peut l'éditer ou le supprimer", on_delete=models.CASCADE)

    youtube_video_id = models.CharField(max_length=255, verbose_name="Id de la vidéo youtube")

    class Meta:
        verbose_name = "Média d'écran de veille"
        verbose_name_plural = "Médias d'écran de veille"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Just a little validation
        """
        assert self.scope == self.PRIVATE_SCOPE or (self.scope == self.PUBLIC_SCOPE and self.owner.is_admin_type()), "Public medias can only be owned by admin user"
        return super().save(*args, **kwargs)    


class ScreensaverBroadcast(models.Model):
    
    customer = models.ForeignKey(Customer, verbose_name="Client", on_delete=models.CASCADE, related_name="screensaver_broadcasts")
    media = models.ForeignKey(ScreensaverMedia, verbose_name="Média", on_delete=models.CASCADE, related_name="screensaver_broadcasts")

    visible = models.BooleanField(verbose_name="Visible", default=False)

    class Meta:
        verbose_name = "Diffusion d'écran de veille"
        verbose_name_plural = "Diffusions d'écran de veille"

    def __str__(self):
        return f"Diffusion de {self.media} chez {self.customer}"
