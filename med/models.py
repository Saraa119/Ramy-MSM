from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from authentication.models import User
from django.contrib.auth.models import AbstractUser, BaseUserManager
import datetime



# from authentication.models import HospitalManager

class Hospital(models.Model):
    name = models.CharField(_("Hospital Name"), max_length = 225, unique=True)
    address = models.TextField(_("Hospital Address"), null=True)
    phone_num = models.IntegerField()
    manager = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('hospital-details', kwargs={'pk' : self.pk})


class Department(models.Model):
    name = models.CharField(_("Department Name"), max_length = 225)
    hospital = models.ForeignKey(Hospital, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name
    

class Equipment(models.Model):
    STATUS = (
        ('LIVE', _("LIVE")),
        ('DOWN', _("DOWN"))
    )
    status = models.CharField(_("Equipment Status"), max_length=50, choices=STATUS, default='LIVE')
    is_approved = models.BooleanField(_("Is approved by manager"), default=True)
    name = models.CharField(_("Equipment Name"), max_length = 225) #unique=True
    specs = models.TextField(_("Technical Specifications and Standards"))
    quantity = models.IntegerField()
    serial_num = models.IntegerField()
    manufacturer = models.CharField(_("Manufacturer"), null=True,max_length = 255)
    country = models.CharField(_("Country"), null=True,max_length = 225)
    model = models.CharField(_("Model"), null=True,max_length = 225)
    risk_level = models.CharField(_("Risk Level"), null=True,max_length = 225)
    eq_class = models.CharField(_("class"), null=True,max_length = 225)
    bio_code = models.CharField(_("BioCode"), null=True, max_length = 225)
    med_agent = models.CharField(_("Medical Agent"),null=True, max_length = 225)
    delivery_date = models.DateField(_("Delivery Date"),null=True)
    warrenty_date = models.DateField(_("End Warrenty Date"),null=True)
    department = models.ForeignKey(Department, null = True, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, null = True, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)



    def __str__(self):
        return self.name
    
    

    def get_absolute_url(self):
        return reverse('equipment-details', kwargs={'pk' : self.pk})    

      

class Procedure(models.Model):
    is_approved = models.BooleanField(_("Is approved by manager"), default=True)
    hospital = models.ForeignKey(Hospital, null = True, on_delete=models.CASCADE)
    physical_condition = models.TextField(_("physical condition"),null=True)
    electrical_safety = models.TextField(_("electrical safety"),null=True)
    preventive_maintenance = models.TextField(_("preventive maintenance "),null=True)
    preformance_testing  = models.TextField(_("preformance testing "),null=True)
    equipment = models.ForeignKey(Equipment,null = True, on_delete=models.CASCADE)


    def __str__(self):
        return self.physical_condition
    
    
    def get_absolute_url(self):
        return reverse('equipment-details', kwargs={'pk' : self.pk})    



###PORT PROXY MODELS INTO NORMAL MODELS, AND USE MULTI INHERITANCE####

class ManagerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.MANAGER)

class EngineerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ENGINEER)

class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.DOCTOR)



class Notifications(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, null=True, on_delete=models.CASCADE)

class Manager(User):
    objects = ManagerManager()
   
    def __str__(self):
        return self.username
        
class Engineer(User):
    is_approved = models.BooleanField(_("Approved"), default=False)
    current_hospital = models.ForeignKey(Hospital, null=True, on_delete=models.SET_NULL)
    department = models.ManyToManyField(Department)
    is_busy = models.BooleanField(_("Busy"), default=False)
    total_orders = models.IntegerField(_("Total Work Orders"), default=0)
    orders_done = models.IntegerField(_("Total Work Orders Done"), default=0)
    start_time = models.IntegerField(default=0)
    total_response_time = models.DurationField(_("Total_Response Time"), default=datetime.timedelta())
    average_response_time = models.DurationField(_("Average_Response Time"), default=datetime.timedelta())
    objects = EngineerManager()

   
    def __str__(self):
        return self.username

class Doctor(User):
    is_approved = models.BooleanField(_("Approved"), default=False)
    current_hospital = models.ForeignKey(Hospital, null=True, on_delete=models.CASCADE) #should it be cascade?
    objects = DoctorManager()
    
    def __str__(self):
        return self.username

class Company(models.Model):
    name = models.CharField(_("Company Name"), max_length = 225)
    email = models.EmailField(_("Company Email"))
    phone_num = models.CharField(_("Phone Number"), max_length=225)
    hospital = models.ForeignKey(Hospital, null=True, on_delete=models.CASCADE) #should it be cascade?
    

    def __str__(self):
        return self.name
        
class EditedEquipment(models.Model):
    eng = models.ForeignKey(Engineer, null = True, on_delete=models.SET_NULL)
    eq_id = models.IntegerField(_("ID of Equiqment to be Edited"))
    STATUS = (
        ('LIVE', _("LIVE")),
        ('DOWN', _("DOWN"))
    )
    status = models.CharField(_("Equipment Status"), max_length=50, choices=STATUS, default='LIVE')
    name = models.CharField(_("Equipment Name"), max_length = 225) #unique=True
    specs = models.TextField(_("Technical Specifications and Standards"))
    quantity = models.IntegerField()
    serial_num = models.IntegerField()
    manufacturer = models.CharField(_("Manufacturer"), null=True,max_length = 255)
    country = models.CharField(_("Country"), null=True,max_length = 225)
    model = models.CharField(_("Model"), null=True,max_length = 225)
    risk_level = models.CharField(_("Risk Level"), null=True,max_length = 225)
    eq_class = models.CharField(_("class"), null=True,max_length = 225)
    bio_code = models.CharField(_("BioCode"), null=True, max_length = 225)
    med_agent = models.CharField(_("Medical Agent"),null=True, max_length = 225)
    delivery_date = models.DateField(_("Delivery Date"),null=True)
    warrenty_date = models.DateField(_("End Warrenty Date"),null=True)
    department = models.ForeignKey(Department, null = True, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, null = True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name