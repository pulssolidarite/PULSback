from django.db import models


class Donator(models.Model):
    email = models.EmailField(blank=True, null=True)
    accept_asso = models.BooleanField(blank=True, null=True, default=False)
    accept_newsletter = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        if self.email:
            return self.email
        return "Donator {}".format(self.pk)
