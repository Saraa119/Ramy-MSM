from django.contrib import admin
from .models import *

admin.site.register(Hospital)
admin.site.register(Department)
admin.site.register(Equipment)
admin.site.register(EditedEquipment)
admin.site.register(Engineer)
admin.site.register(Doctor)
admin.site.register(Notifications)