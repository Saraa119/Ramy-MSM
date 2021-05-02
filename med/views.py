from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView
from .models import Engineer, Hospital, Doctor, Procedure , Equipment, Manager, Notifications, Department, Company, EditedEquipment
from .forms import HospitalForm, CreateCompanyForm, UploadJsonForm
from django.urls import reverse_lazy
from django.db.models import Q
from med.forms import JoinHospitalForm
from authentication.models import User
from workflow.models import Ticket 
import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
import datetime
from xhtml2pdf import pisa
import json
from django.contrib import messages


class SearchHospitalView(LoginRequiredMixin, ListView):
    model = Hospital
    template_name = 'med/hospital_search.html'

    def get_queryset(self):
        object_list = Hospital.objects.all()
        return object_list

class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'med/equipment_list.html'

    def get_queryset(self):
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            eng_hos = eng.current_hospital 
            object_list = eng_hos.equipment_set.all()
            # object_list = [eq for q1 in dep_list for eq in q1.equipment_set.all()]
            return object_list
        elif(self.request.user.type == 'DOCTOR'):
            doc = Doctor.objects.get(id = self.request.user.id)
            doc_hos = doc.current_hospital 
            object_list = doc_hos.equipment_set.all()
            # object_list = [eq for q1 in dep_list for eq in q1.equipment_set.all()]
            return object_list
        else:
            man = Manager.objects.get(id = self.request.user.id)
            object_list = man.hospital.equipment_set.all()
            # object_list = [eq for q1 in dep_list for eq in q1.equipment_set.all()]
            return object_list
    # The .get_context_data(..) method [Django-doc] returns a dictionary that contains the context that will be passed to the template for rendering.
    #A ListView [Django-doc] will by default make a dictionary with keys and values
    def get_context_data(self, **kwargs):
        # super() make me inherit from My class(EquipmentListView)
        context = super(EquipmentListView, self).get_context_data(**kwargs)
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            context['eng'] = eng 
        return context

class EditedEquipmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = EditedEquipment
    template_name = 'med/edits_list.html'

    def get_queryset(self):
        man = Manager.objects.get(id = self.request.user.id)
        object_list = man.current_hospital.editedequipment_set.all()
        return object_list
    #checking if user passes test....
    def test_func(self):
        return self.request.user.type == 'MANAGER'


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'med/department_list.html'

    def get_queryset(self):
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            eng_hos = eng.current_hospital 
            object_list = eng_hos.department_set.all()
            return object_list
        elif(self.request.user.type == 'DOCTOR'):
            doc = Doctor.objects.get(id = self.request.user.id)
            doc_hos = doc.current_hospital 
            object_list = doc_hos.department_set.all()
            return object_list
        else:
            man = Manager.objects.get(id = self.request.user.id)
            object_list = man.hospital.department_set.all()
            return object_list

    def get_context_data(self, **kwargs):
        context = super(DepartmentListView, self).get_context_data(**kwargs)
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            context['eng'] = eng 
        return context
            



class  SearchHospitalResultsView(LoginRequiredMixin, ListView):
    model = Hospital
    template_name = 'med/hospital_search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Hospital.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )
        return object_list


class HospitalDetailsView(LoginRequiredMixin, DetailView):
    model = Hospital 
    template_name = 'med/hospital_details.html'
    # form_class = RequestJoinForm
    # success_url = reverse_lazy('home')
    context_object_name = 'hospital'


    #can I send a specific context here ??

    # def form_valid(self, form):
    #     eng = Engineer.objects.get(id = self.request.user.id)
    #     print(form.cleaned_data['department'])
    #     print("here")
    #     eng.department = form.cleaned_data['department']
    #     eng.save()
    #     return super().form_valid(form)

class EquipmentDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Equipment 
    template_name = 'med/equipment_details.html'
    context_object_name = 'equipment'
    #can I send a specific context here ??

    def get_context_data(self, **kwargs):
        context = super(EquipmentDetailsView, self).get_context_data(**kwargs)
        context['equipment'] = Equipment.objects.get(id = self.kwargs['pk'])
        try:
            context['ticket'] = Ticket.objects.get(Q(equipment = Equipment.objects.get(id = self.kwargs['pk'])), Q(status = 'OPEN'))
            context['engineer'] = Engineer.objects.get(id = self.request.user.id)
        except:
            pass
        return context
    
    def test_func(self):
        eq = Equipment.objects.get(id = self.kwargs['pk'])
        if eq.is_approved:
            if self.request.user.type == 'ENGINEER':
                eng = Engineer.objects.get(id = self.request.user.id)
                if not self.get_object().department in eng.department.all():
                    return False
                return True 
            return True
        return False

class EquipmentProcedureView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Equipment 
    template_name = 'med/equipment_procedure.html'
    context_object_name = 'equipment'
    #can I send a specific context here ??

    def get_context_data(self, **kwargs):
        context = super(EquipmentProcedureView, self).get_context_data(**kwargs)
        context['equipment'] = Equipment.objects.get(id = self.kwargs['pk'])
        try:
            context['ticket'] = Ticket.objects.get(Q(equipment = Equipment.objects.get(id = self.kwargs['pk'])), Q(status = 'OPEN'))
            context['engineer'] = Procedure.objects.get(id = self.request.user.id)
        except:
            pass
        return context
    
    def test_func(self):
        eq = Equipment.objects.get(id = self.kwargs['pk'])
        if eq.is_approved:
            if self.request.user.type == 'ENGINEER':
                eng = Engineer.objects.get(id = self.request.user.id)
                if not self.get_object().department in eng.department.all():
                    return False
                return True 
            return True
        return False


class PreApprovedEquipmentDetails(LoginRequiredMixin, DetailView):
    model = Equipment 
    template_name = 'med/pre_approved_equipment_details.html'
    context_object_name = 'equipment'

    def get_context_data(self, **kwargs):
        context = super(PreApprovedEquipmentDetails, self).get_context_data(**kwargs)
        context['equipment'] = Equipment.objects.get(id = self.kwargs['pk'])
        return context
    
class DepartmentDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Department 
    template_name = 'med/department_details.html'
    context_object_name = 'department'
    #can I send a specific context here ??

    def get_context_data(self, **kwargs):
        context = super(DepartmentDetailsView, self).get_context_data(**kwargs)
        context['department'] = Department.objects.get(id = self.kwargs['pk'])
        return context
    
    def test_func(self):
        if self.request.user.type == 'ENGINEER':
            eng = Engineer.objects.get(id = self.request.user.id)
            if not self.get_object() in eng.department.all():
                return False
            return True 
        return True 


def JoinHospitalView(request, uid):
    man = Manager.objects.get(id = request.user.id)
    user = User.objects.get(id = uid)
    try:
        eng = Engineer.objects.get(id = uid)
        eng.is_approved = True 
        eng.current_hospital = man.hospital
        user.in_hospital = True
        Notifications.objects.get(user = user).delete() 
        eng.save()
        user.save()
        return redirect('home')
    except:
        doc = Doctor.objects.get(id = uid)
        doc.is_approved = True 
        doc.current_hospital = man.hospital        
        user.in_hospital = True 
        Notifications.objects.get(user = user).delete() 
        doc.save()
        user.save()
        return redirect('home')

def RequestJoinHospitalView(request, hid, uid):
    user = User.objects.get(id = uid)
    hospital = Hospital.objects.get(id = hid)
    messages.success(request, f'A request to join hospital has been sent...')
    try :
        #check if user already submitted a request, and delete it if he did
        Notifications.objects.get(user=user).delete()
        #create new notification
        Notifications.objects.create(user=user, hospital=hospital)
        return redirect('home')
    except:
        #if he didn't already have a request, just create a new one
        Notifications.objects.create(user=user, hospital=hospital)
        return redirect('home')
        
# Manager Notifications
class NotificationsListView(LoginRequiredMixin, ListView):
    model = Notifications
    template_name = 'med/list_notifications.html'

    def get_queryset(self):
        man_hos = Manager.objects.get(id = self.request.user.id).hospital
        object_list = Notifications.objects.filter(hospital=man_hos)
        return object_list

    
class CreateHospitalView(LoginRequiredMixin, CreateView):
    model = Hospital
    template_name = 'med/register_hospital.html'
    form_class = HospitalForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)

class List_Create_CompanyView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'med/list_create_company.html'
    form_class = CreateCompanyForm
    success_url = reverse_lazy('list-create-company')

    def form_valid(self, form):
        eng_hos = Engineer.objects.get(id = self.request.user.id).current_hospital
        form.instance.hospital = eng_hos
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        eng_hos = Engineer.objects.get(id = self.request.user.id).current_hospital
        context["companies"] = Company.objects.filter(hospital = eng_hos)
        return context

def generate_PDF(request, pk):
    data = {}
    data['ticket'] = Ticket.objects.get(id = pk)
    template = get_template('workflow/ticket_details.html')
    html  = template.render(data)

    file = open('test.pdf', "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()            
    return HttpResponse(pdf, 'application/pdf')

def handle_uploaded_file(request, f):
    man = Manager.objects.get(id = request.user.id)
    # wb+ does create the file from scratch
    with open('hospital_data.json', 'wb+') as data:
        for chunk in f.chunks():
            data.write(chunk)

    with open('hospital_data.json', 'r') as read_file:
        data = json.load(read_file)
    
    for dep in data['departments']:   
        for dep_name in dep:
            new_dep = Department.objects.create(name=dep_name, hospital = man.hospital)
            new_dep.save()
            for equip in dep[dep_name]['Equipment']:
                new_equip = Equipment.objects.create(name = equip['name'],
                                                     specs = equip['specs'],
                                                     quantity = equip['quantity'],
                                                     serial_num = equip['serial_num'], 
                                                     manufacturer = equip['manufacturer'],
                                                     country = equip['country'],
                                                     model = equip['model'],
                                                     risk_level = equip['risk_level'],
                                                     eq_class = equip['eq_class'],
                                                     bio_code = equip['bio_code'],
                                                     med_agent = equip['med_agent'],
                                                     delivery_date = equip['delivery_date'],
                                                     warrenty_date = equip['warrenty_date'],
                                                     department = new_dep, 
                                                     hospital = man.hospital)
                new_equip.save()



def upload_json(request):
    if request.method == 'POST':
        form = UploadJsonForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request, request.FILES['file'])
            return redirect('home')
    else:
        form = UploadJsonForm()
    return render(request, 'med/upload_json.html', {'form': form})


def welcome(request):
    return render(request,'dashboard/welcome.html')