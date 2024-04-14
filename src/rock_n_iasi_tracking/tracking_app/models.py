from django.db import models
import uuid
import datetime


# Create your models here.

class Participant(models.Model):
    qrcode_id = models.UUIDField(null=False, unique=True)
    first_name = models.CharField(null=True, max_length=100)
    last_name = models.CharField(null=True, max_length=100)
    inside = models.BooleanField(default=False)
    date_entered = models.DateTimeField(auto_now=True)

class QrCodeId(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    is_used = models.BooleanField(default=False)

class Entry(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    exit = models.BooleanField(default=False)