from django.contrib import admin

from signup.models import Slot, Signup, GroupMembership

admin.site.register(Slot)
admin.site.register(Signup)
admin.site.register(GroupMembership)

