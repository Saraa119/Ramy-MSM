from django import forms
from .models import Ticket
from med.models import Equipment
from med.models import Department, Doctor, EditedEquipment, Engineer, Manager, Procedure
from django.shortcuts import get_object_or_404


class CustomMCF(forms.ModelChoiceField):
    def label_from_instance(self, equipment):
        """
        Convert objects into strings and generate the labels for the choices
        presented by this object. Subclasses can override this method to
        customize the display of the choices.
        """
        return f'{equipment.name}, {equipment.department.name}'

class ENGCustomMCF(forms.ModelChoiceField):
    def label_from_instance(self, engineer):
        return f'{engineer.first_name} {engineer.last_name}'

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        doc_hos = get_object_or_404(Doctor,id = self.request.user.id).current_hospital
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['equipment'].queryset = doc_hos.equipment_set.filter(status = 'LIVE') 

    class Meta:
        model = Ticket
        fields = ['equipment', 'ticket_type', 'details']

    
    
    
    ticket_type = forms.ChoiceField(
        choices=Ticket.types,
        widget = forms.Select
    )

   
    # img = forms.ImageField()
    details = forms.Textarea()

    equipment = CustomMCF(
        queryset= None, 
        widget = forms.Select
    )


class TicketFormID(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_type', 'details']
    
    
    ticket_type = forms.ChoiceField(
        choices=Ticket.types,
        widget = forms.Select
    )

    # img = forms.ImageField()
    details = forms.Textarea()



class AssignEng(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        man = Manager.objects.get(id = self.request.user.id)
        super(AssignEng, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = man.hospital.engineer_set.filter(department = self.instance.equipment.department)

    class Meta:
        model = Ticket
        fields = ['user']
    
    user = ENGCustomMCF(
        queryset= None, 
        widget = forms.Select
    )
    
class AssignDepartment(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        man = Manager.objects.get(id = self.request.user.id)
        super(AssignDepartment, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = man.hospital.department_set.all()

    class Meta:
        model = Engineer
        fields = ['department']
    
    department = forms.ModelMultipleChoiceField(
        queryset=None, 
        widget=forms.CheckboxSelectMultiple
    )

class AddDepartmentForm(forms.ModelForm):
    
    class Meta:
        model = Department
        fields = ['name']
    
    name = forms.CharField(max_length=100)

class DepartmentUpdateForm(forms.ModelForm):

    class Meta:
        model = Department 
        fields = ['name']

class EquipmentUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.deps = kwargs.pop("deps")
        super(EquipmentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = self.deps

    class Meta:
        model = Equipment 
        fields = ['name', 'specs', 'quantity', 'serial_num', 'manufacturer', 'country', 'model', 'risk_level', 'eq_class', 'bio_code', 'med_agent', 'delivery_date', 'warrenty_date','department']

    department = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select
    )
class AddEquipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        eng = Engineer.objects.get(id = self.request.user.id)
        super(AddEquipmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = eng.department.all() 
    
    class Meta:
        model = Equipment
        fields = ['name', 'specs', 'quantity', 'serial_num', 'manufacturer', 'country', 'model', 'risk_level', 'eq_class', 'bio_code', 'med_agent', 'delivery_date', 'warrenty_date','department']
    
    name = forms.CharField(max_length=100)
    specs = forms.Textarea()
    quantity = forms.IntegerField()
    serial_num = forms.IntegerField()

    department = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select
    )

class AddProcedureForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        eng = Engineer.objects.get(id = self.request.user.id).current_hospital
        super(AddProcedureForm, self).__init__(*args, **kwargs)    
        self.fields['equipment'].queryset = eng.equipment_set.filter(status = 'LIVE')
        #self.fields['equipment'].queryset = doc_hos.equipment_set.filter(status = 'LIVE') 
        #doc_hos = get_object_or_404(Doctor,id = self.request.user.id).current_hospital
        #super(TicketForm, self).__init__(*args, **kwargs)
        #self.fields['equipment'].queryset = doc_hos.equipment_set.filter(status = 'LIVE')

    class Meta:
        model = Procedure
        fields = ['physical_condition', 'electrical_safety', 'preventive_maintenance', 'preformance_testing','equipment']
    
    physical_condition = forms.Textarea()
    electrical_safety  = forms.Textarea()
    preventive_maintenance = forms.Textarea()
    preformance_testing = forms.Textarea()

    equipment = CustomMCF(
        queryset= None, 
        widget = forms.Select
    )

class AddEditedEquipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        pk = kwargs.pop('pk')
        eq = Equipment.objects.get(id = pk)
        eng = Engineer.objects.get(id = self.request.user.id)
        super(AddEditedEquipmentForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = eng.department.all() 
        self.fields['name'].initial = eq.name
        self.fields['specs'].initial = eq.specs
        self.fields['quantity'].initial = eq.quantity
        self.fields['serial_num'].initial = eq.serial_num
        self.fields['manufacturer'].initial = eq.manufacturer
        self.fields['country'].initial = eq.country
        self.fields['model'].initial = eq.model
        self.fields['risk_level'].initial = eq.risk_level
        self.fields['eq_class'].initial = eq.eq_class
        self.fields['bio_code'].initial = eq.bio_code
        self.fields['med_agent'].initial = eq.med_agent
        self.fields['delivery_date'].initial = eq.delivery_date
        self.fields['warrenty_date'].initial = eq.warrenty_date
        self.fields['department'].initial = eq.department
    
    class Meta:
        model = EditedEquipment
        fields = ['name', 'specs', 'quantity', 'serial_num', 'manufacturer', 'country', 'model', 'risk_level', 'eq_class', 'bio_code', 'med_agent', 'delivery_date', 'warrenty_date','department']
    
    name = forms.CharField(max_length=100)
    specs = forms.Textarea()
    quantity = forms.IntegerField()
    serial_num = forms.IntegerField()

    department = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select
    )

class AddEquipmentIDForm(forms.ModelForm):

    class Meta:
        model = Equipment
        fields = ['name', 'specs', 'quantity', 'serial_num', 'manufacturer', 'country', 'model', 'risk_level', 'eq_class', 'bio_code', 'med_agent', 'delivery_date', 'warrenty_date']
    
    name = forms.CharField(max_length=100)
    specs = forms.Textarea()
    quantity = forms.IntegerField()
    serial_num = forms.IntegerField()
