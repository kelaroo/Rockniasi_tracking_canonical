import datetime
from django.core.files.utils import FileProxyMixin
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .forms import LoginForm, ParticipantForm, EntryForm, QrcodeEditForm
from .models import Participant, QrCodeId, Entry
import uuid

# Util
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

# Create your views here.

def index_view(request):
    if not request.user.is_authenticated:       
        return redirect('login')

    participants = Participant.objects.all().filter(date_entered__date=datetime.datetime.today())
    total = participants.count
    inside = participants.filter(inside=True).count

    return render(request, 'tracking_app/index.html', {
        'totalNr': total,
        'inside': inside,
    })
    
def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"],
                password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Invalid username or password")

    return render(request, 'tracking_app/login.html', {
        'form': form
        })

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(redirect_field_name='login')
def new_participant_view(request):
    form = ParticipantForm(request.POST or None)
    
    context = {'form': form}

    if request.method == "POST":
        if form.is_valid():
            copil = form.save()
            copil.inside = True
            copil.save()
            last_name = form.cleaned_data['last_name']
            #first_name = form.cleaned_data['first_name']
            context['name'] = "%d %s" % (copil.id, last_name)
            form = ParticipantForm()
    
    return render(request, 'tracking_app/new_participant.html', context)

@login_required(redirect_field_name='login')
def participants_view(request):
    participants = Participant.objects.all().order_by('last_name')

    return render(request, 'tracking_app/participants.html', {
        'participants': participants
    })

@login_required(redirect_field_name='login')
def edit_participant_view(request, id):
    try:
        participant = Participant.objects.get(pk=id)
    except Participant.DoesNotExist:
        return HttpResponse("404 Particpant with id '%s' does not exist"%id)
    
    form = QrcodeEditForm(request.POST or None)

    context = {}

    if request.method == 'POST':
        if form.is_valid():
            qrcodeid = form.cleaned_data['qrcode_uuid']
            try:
                participant = Participant.objects.get(qrcode_id=qrcodeid)
            except:
                entry_set = Entry.objects.all().filter(participant=participant).order_by('time')
                entries = {}
                for entry in entry_set:
                    date = entry.time.strftime("%d %b %Y")
                    if date not in entries:
                        entries[date] = []
                    entries[date].append(entry)
                return render(request, 'tracking_app/edit_participant.html', {
                    'participant': participant,
                    'entries': entries.items(),
                    'form': form,
                    'message': "Invalid qrcode"
                })
            participant.qrcode_id = qrcodeid
            participant.save()
            context['message'] = "Qrcode changed"
        else:
            context['message'] = "Invalid qrcode"
    entry_set = Entry.objects.all().filter(participant=participant).order_by('time')
    entries = {}
    for entry in entry_set:
        date = entry.time.strftime("%d %b %Y")
        if date not in entries:
            entries[date] = []
        entries[date].append(entry)
    print(entries)

    context['participant'] = participant
    context['entries'] = entries.items()
    context['form'] = form
    return render(request, 'tracking_app/edit_participant.html', context)

@login_required(redirect_field_name='login')
def participant_entry_view(request):
    form = EntryForm(request.POST or None)
    context = {'form': form}

    if request.method == "POST":
        if form.is_valid():
            try:
                participant = Participant.objects.get(qrcode_id=form.cleaned_data['qrcode_uuid'])
            except Participant.DoesNotExist:
                form.add_error(None, "Invalid code")
                return render(request, 'tracking_app/entry.html', context)
            participant.inside = not participant.inside
            participant.date_entered = datetime.datetime.today()
            participant.save()
            Entry.objects.create(participant=participant, exit=not participant.inside)
            context['succes'] = '%d %s %s has %s' % (
                participant.id,
                participant.last_name,
                participant.first_name,
                'entered' if participant.inside else 'exited')
            if participant.inside:
                context['succes'] = '<div style="color:green;">' + context['succes'] + '</div>'
            else:
                context['succes'] = '<div style="color:red;">' + context['succes'] + '</div>'

    return render(request, 'tracking_app/entry.html', context)

@login_required(redirect_field_name='login')
def delete_participant_view(request, id):
    copil = get_object_or_404(Participant, pk=id)
    qrcodeid = QrCodeId.objects.get(pk = copil.qrcode_id)
    qrcodeid.is_used = False
    qrcodeid.save()
    copil.delete()
    return redirect('participants')