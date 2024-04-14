from django import forms
from django.contrib.auth.models import User
from django.forms import fields, widgets

from .models import Participant, Entry
import asyncio

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ('qrcode_id', 'last_name')
        widgets = {
            #'qrcode_id': forms.HiddenInput()
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['last_name'].widget.attrs.update(autofocus='autofocus')

class EntryForm(forms.Form):
    qrcode_uuid = forms.UUIDField()

class QrcodeEditForm(forms.Form):
    qrcode_uuid = forms.UUIDField()