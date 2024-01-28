from django.contrib import admin

from terminal.models import Donator, Session

from .payment import PaymentAdmin
from .terminal import TerminalAdmin

# Register your models here.
admin.site.register(Donator)
admin.site.register(Session)
