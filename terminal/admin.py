from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Terminal)
admin.site.register(Donator)
admin.site.register(Session)
admin.site.register(Payment)