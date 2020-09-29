from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Game)
admin.site.register(Core)
admin.site.register(GameFile)
admin.site.register(CoreFile)