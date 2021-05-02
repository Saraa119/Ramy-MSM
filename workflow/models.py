from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.models import User
# from multiselectfield import MultiSelectField
from med.models import Doctor, Engineer, Equipment , Hospital
import datetime

class Ticket(models.Model):
    types = (
                ('REPAIR', _('Repairment of Equipment')), 
                ('TRANSFER', _('Transfer of Equipment')), 
                ('TRAINING', _('Training of using Equipment'))
            )
    STATUS = (
        ('OPEN', _('Open Issue')),
        ('CLOSED', _('Closed Issue'))
    )
    
    ticket_type = models.CharField(_("Type"), max_length = 50, choices = types, default='REPAIR')
    submitter =  models.ForeignKey(Doctor, null = True, on_delete=models.SET_NULL)
    user = models.ForeignKey(Engineer, null = True, on_delete=models.SET_NULL)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    status = models.CharField(_("Status"), max_length = 50, choices = STATUS, default='OPEN')
    response_time = models.DurationField(_("Reponse Time"), default=datetime.timedelta(0))
    details = models.TextField(_("Problem Details"), null=True)
    # img = models.ImageField(_("Equipment Picture"), upload_to='tickets_images', null=True)

    def __str__(self):
        return self.submitter.username

