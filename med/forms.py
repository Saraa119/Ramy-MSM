from django import forms
# from authentication.models import 
from .models import Department, Equipment, Engineer, Hospital, Company , Procedure


class CustomMMCF(forms.ModelMultipleChoiceField):
    def label_from_instance(self, equipment):
        return f'{equipment.name}--{equipment.belongs_to}'

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'phone_num']

    name = forms.CharField()
    address = forms.Textarea()
    phone_num = forms.IntegerField()

    # departments = forms.ModelMultipleChoiceField(
    #     queryset=Department.objects.all(),
    #     widget = forms.CheckboxSelectMultiple)
    
    # equipment = CustomMMCF(
    #     queryset=Equipment.objects.all(),
    #     widget = forms.CheckboxSelectMultiple)
        

class JoinHospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['username']
    username = forms.CharField()    
   
class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone_num']
    
    name = forms.CharField()
    email = forms.EmailField()
    phone_num = forms.CharField()

class UploadJsonForm(forms.Form):
    file = forms.FileField()

