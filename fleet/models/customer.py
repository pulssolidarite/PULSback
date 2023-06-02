from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.conf import settings


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customer",
        null=True,
    )  # TODO assign user to every customers then set this field to null=False

    company = models.CharField(max_length=255)
    representative = models.CharField(max_length=255, null=True)
    logo = models.FileField(blank=True, null=True, upload_to="customers/logos/")
    sales_type = models.CharField(max_length=1, default="A", null=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    can_edit_featured_content = models.BooleanField(default=False)
    can_edit_donation_formula = models.BooleanField(default=False)
    can_edit_donation_amount = models.BooleanField(default=False)
    can_edit_screensaver_broadcasts = models.BooleanField(default=False)
    can_see_donators = models.BooleanField(default=False)

    # The customer can select its own featured campaign for its own terminals
    # This selected campaign will overwrite the campaign that is selected as featured for everyone
    featured_campaign = models.ForeignKey(
        "fleet.Campaign", on_delete=models.SET_NULL, null=True, blank=True
    )

    # The customer can select its own featured game for its own terminals
    # This selected game will overwrite the game that is selected as featured for everyone
    featured_game = models.ForeignKey(
        "game.Game", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ["id"]

    def __str__(self):
        return self.company or ""


@receiver(post_delete, sender=Customer)
def post_delete_user(sender, customer: Customer, *args, **kwargs):
    if customer.user:  # just in case user is not specified
        customer.user.delete()
