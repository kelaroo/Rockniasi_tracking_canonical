from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Participant)
admin.site.register(QrCodeId)
admin.site.register(Entry)