from django.db import models
import pytz

eastern = pytz.timezone('US/Eastern')
class Slot(models.Model):
    time = models.DateTimeField('timeslot')
    def __unicode__(self):
        return self.time.astimezone(eastern).strftime('%d %b@%H:%M')

class Signup(models.Model):
    slot = models.ForeignKey(Slot)
    group_id = models.CharField(max_length=200)
    signup_watid = models.CharField(max_length=200)
    signup_time = models.DateTimeField('date signed up', auto_now_add=True)
    def str_without_slot(self):
        signup_time_str = self.signup_time.astimezone(eastern).strftime('%d %b %H:%M')
        return '{0} ({1}@{2})'.format(self.group_id, 
                                      self.signup_watid, 
                                      signup_time_str)
    def __unicode__(self):
        return unicode(self.slot) + ': ' + self.str_without_slot()

class GroupMembership(models.Model):
    watid = models.CharField(max_length=80)
    group_id = models.CharField(max_length=80)
    def __unicode__(self):
        return '{0} in {1}'.format(self.watid, self.group_id)


