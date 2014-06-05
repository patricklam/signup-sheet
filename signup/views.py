import re
from django.shortcuts import render
from signup.models import Slot, Signup, GroupMembership

def find_group(user):
    return GroupMembership.objects.filter(watid=user).first().group_id if GroupMembership.objects.filter(watid=user).exists() else 'None'

def is_member(user, group):
    return GroupMembership.objects.filter(watid=user).exists() and group == GroupMembership.objects.filter(watid=user).first().group_id

def can_release(uid, slot, as_superuser):
    rv = False
    taken = slot.signup_set.exists()
    if taken: rv = is_member(uid, slot.signup_set.first().group_id) or as_superuser
    return rv

release_re = re.compile('release_([0-9]+)')
request_re = re.compile('request_([0-9]+)')
def index(request):
    params = request.POST
    uid = request.user.username
    as_superuser = request.user.is_superuser and not('fake' in params and params['fake'] != '')
    if request.user.is_superuser and 'fakewatid' in params and params['fakewatid'] != '': 
        uid = params['fakewatid']
    slot_list = Slot.objects.all()
    info = []

    already_have_one = False
    for slot in slot_list:
        if slot.signup_set.exists() and is_member(uid, slot.signup_set.first().group_id):
            already_have_one = True

    for key, value in params.iteritems():
        rel = release_re.match(key)
        if rel:
            slot_id = rel.group(1)
            slot = Slot.objects.filter(id=slot_id).first()
            if (can_release(uid, slot, as_superuser)): 
                signup_id = slot.signup_set.first().id
                Signup.objects.filter(id=signup_id).delete()
                already_have_one = False
        req = request_re.match(key)
        if req:
            slot_id = req.group(1)
            slot = Slot.objects.filter(id=slot_id).first()
            taken = slot.signup_set.exists()
            if not taken and not already_have_one and request.user.is_authenticated: 
                Signup(slot=slot, group_id=find_group(uid),
                       signup_watid=uid).save()

    for slot in slot_list:
        taken = slot.signup_set.exists()

        allowed_options = ''
        if can_release(uid, slot, as_superuser): 
            allowed_options += '<input type="submit" name="release_{0}" value="Release">'.format(slot.id)
        if not taken and not already_have_one and request.user.is_authenticated:  
            allowed_options += '<input type="submit" name="request_{0}" value="Request">'.format(slot.id)

        info.append((slot,
                     slot.signup_set.get().str_without_slot() if taken else '',
                     allowed_options))
    context = {'info': info, 
               'who' : uid,
               'effective_who': 'root' if as_superuser else uid, 
               'asroot': 'checked' if not as_superuser else ''}
    return render(request, 'signup/index.html', context)

from datetime import datetime, timedelta
import pytz
import string
import random

def init(request):
    if not request.user.is_superuser: return render(request, 'signup/index.html', {})

    params = request.POST
    msgs = ''

    if 'slots' in params and params['slots'] == 'reset':
        eastern=pytz.timezone('US/Eastern')
        Slot.objects.all().delete()
        for d in range(0,3):
            for t in range(0,6):
                Slot(time=(eastern.localize(datetime(2014,6,18,10,30)) + timedelta(minutes=t*20) + timedelta(days=d*7))).save()
        msgs = msgs + "Re-initialized slots.<br />"

    if 'groupinfo' in params and len(params['groupinfo']) > 0:
        GroupMembership.objects.all().delete()
        ext = '.txt'; group_count = 0; student_count = 0
        for line in params['groupinfo'].splitlines():
            # could also have used a regexp below
            if (line.count(':') != 2): continue
            group_namet, dummy, users = map(lambda x: x.strip(), line.split(':'))
            if (not (group_namet.endswith(ext))): msgs.append('Ignoring line {0}<br>'.format(line)); continue
            group_name = group_namet[0:len(group_namet)-len(ext)]
            if (dummy != 'Group UW userids'): msgs.append('Ignoring line {0}<br>'.format(line)); continue
            user_list = map(lambda x: x.strip(), users.split(','))
            group_count = group_count + 1
            for user in user_list:
                GroupMembership(watid = user, group_id = group_name).save()
                student_count = student_count + 1
        msgs = msgs + \
            'Success! Added {0} groups with {1} students.<br />'.format(group_count,
                                                                        student_count)
    if 'signups' in params:
        if (params['signups'] == 'reset'):
            Signup.objects.all().delete()
            msgs = msgs + 'Cleared signups.<br />'
        if (params['signups'] == 'dummy'):
            Signup.objects.all().delete()

            all_slots = []
            for s in Slot.objects.all(): all_slots.append(s)
            random.shuffle(all_slots)

            all_gms = []
            for gm in GroupMembership.objects.all(): all_gms.append(gm)
            random.shuffle(all_gms)

            for s in range(0,18):
                Signup(slot=all_slots[s], group_id=all_gms[s].group_id, 
                       signup_watid=all_gms[s].watid).save()
                # also, go through and remove all future refs to group that just got added.
                for i in range(s+1, len(all_gms)):
                    while (i < len(all_gms) and all_gms[s].group_id == all_gms[i].group_id):
                        all_gms.remove(all_gms[i])
            msgs = msgs + 'Populated with dummy signups.<br />'

    return render(request, 'signup/init.html', {'msgs': msgs})
