from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DetailView 
from workflow.models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from .forms import TicketForm, TicketFormID, AssignEng, AddDepartmentForm, AddEquipmentForm, DepartmentUpdateForm, EquipmentUpdateForm, AddEquipmentIDForm, AssignDepartment, AddEditedEquipmentForm ,AddProcedureForm
from django.urls import reverse_lazy
from med.models import Department, Doctor, Engineer, Equipment, Manager, EditedEquipment, Procedure
from authentication.models import User
import time, datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from hospital.settings import EMAIL_FROM_ADDRESS
from django.contrib import messages



class Submit_Ticket(LoginRequiredMixin, CreateView):
    model = Ticket
    template_name = 'workflow/submit_ticket.html'
    form_class = TicketForm
    context_object_name = 'ticket' 
    success_url = reverse_lazy('home') #reverse_lazy() returns an object

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super(Submit_Ticket, self).get_form_kwargs()
        #**kwargs allows you to handle named arguments that you have not defined in advance
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        """If the form is valid, redirect to the supplied URL."""
        form.instance.submitter = Doctor.objects.get(id = self.request.user.id)
        # doc = Doctor.objects.get(id = self.request.user.id)
        doc = get_object_or_404(Doctor, id = self.request.user.id)
        doc_hos = doc.current_hospital
        eq = doc_hos.equipment_set.filter(name = form.instance.equipment).first()
        eq.status = 'DOWN'
        eq.save()
        # form.save()
        # form.instance.status = 'DOWN'
        return super().form_valid(form) 


class Submit_Ticket_Using_Id(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Ticket
    template_name = 'workflow/submit_ticket_id.html'

    form_class = TicketFormID
    context_object_name = 'ticket' 
    success_url = reverse_lazy('home')
    # redirect_field_name = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.submitter = Doctor.objects.get(id = self.request.user.id)
        eq = Equipment.objects.get(id = self.kwargs['pk'])
        eq.status = 'DOWN'
        eq.save()
        form.instance.equipment = Equipment.objects.get(id = self.kwargs['pk'])
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.type == 'DOCTOR' 
    
    def dispatch(self, request, *args, **kwargs):
        #dispatch Think of it as a middleman between requests and responses.
        if request.user.is_authenticated and request.user.type == 'DOCTOR':
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('equipment-details', pk=self.kwargs['pk'])

def sortFunc(e):
        return e.id
class List_Tickets(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'workflow/list_tickets.html'
    
    

    def queryset(self):
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            eng_hos = eng.current_hospital 
            dep_list = eng_hos.department_set.all()
            # ordering by the newest id
            object_list = [ticket for q1 in dep_list for eq in q1.equipment_set.all() for ticket in eq.ticket_set.all().order_by('-id')]
            return object_list
        elif(self.request.user.type == 'DOCTOR'):
            doc = Doctor.objects.get(id = self.request.user.id)
            doc_hos = doc.current_hospital 
            dep_list = doc_hos.department_set.all()
            object_list = [ticket for q1 in dep_list for eq in q1.equipment_set.all() for ticket in eq.ticket_set.all().order_by('-id')]
            return object_list
        else:
            man = Manager.objects.get(id = self.request.user.id)
            dep_list = man.hospital.department_set.all()
            object_list = [ticket for q1 in dep_list for eq in q1.equipment_set.all() for ticket in eq.ticket_set.all().order_by('-id')]
            return object_list
    
    def get_context_data(self, **kwargs):
        context = super(List_Tickets, self).get_context_data(**kwargs)
        if(self.request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = self.request.user.id)
            context['eng'] = eng 
        return context

class Ticket_Details(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'workflow/ticket_details.html'

    def get_context_data(self, **kwargs):
        context = super(Ticket_Details, self).get_context_data(**kwargs)
        context['ticket'] = Ticket.objects.get(id = self.kwargs['pk'])
        try:
            context['engineer'] = Engineer.objects.get(id = self.request.user.id)
        except:
            pass
        return context

class Assign_Engineer(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = 'workflow/assign.html'
    form_class = AssignEng
    success_url = reverse_lazy('list-tickets')

    def get_form_kwargs(self):
        kwargs = super(Assign_Engineer, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        #subtract total work orders by 1 from current engineer if he is there
        eng = form.instance.user
        eng.is_busy = True 
        eng.total_orders += 1
        eng.save()

        user = Ticket.objects.get(id = self.kwargs['pk']).user
        if user :
            user.total_orders -= 1
            user.save()
        
        send_mail('Work order',
                'you have a new work order, please check it: https://hospital-msm.herokuapp.com/workflow/engineer_work/', 
                EMAIL_FROM_ADDRESS,
                [eng.email])
        return super().form_valid(form)

class Assign_Department(LoginRequiredMixin, UpdateView):
    model = Engineer
    template_name = 'workflow/assign_department.html'
    form_class = AssignDepartment
    success_url = reverse_lazy('list-employees')

    def get_form_kwargs(self):
        kwargs = super(Assign_Department, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
    
class Engineer_Work(LoginRequiredMixin, ListView):
    model = Ticket 
    template_name = 'workflow/eng_work.html'

    def get_queryset(self):
        eng = Engineer.objects.get(id = self.request.user.id)
        object_list = eng.ticket_set.all().order_by('-id')
        return object_list
    
    def get_context_data(self, **kwargs):
        context = super(Engineer_Work, self).get_context_data(**kwargs)
        context['engineer'] = Engineer.objects.get(id = self.request.user.id)
        return context

class List_Employees(LoginRequiredMixin, ListView):
    model = User
    template_name ='workflow/list_employees.html'

    def get_queryset(self):
        current_man = Manager.objects.get(id = self.request.user.id)
        engs = current_man.hospital.engineer_set.all()
        docs = current_man.hospital.doctor_set.all()
        object_list = [eng for eng in engs]
        object_list += [doc for doc in docs]
        return object_list

class Staff_Response(LoginRequiredMixin, ListView):
    model = User
    template_name ='workflow/staff_response.html'

    def get_queryset(self):
        current_man = Manager.objects.get(id = self.request.user.id)
        engs = current_man.hospital.engineer_set.all()
        object_list = [eng for eng in engs]
        return object_list


def Work_Process(request, pk, pk2):
    eng = Engineer.objects.get(id = request.user.id)
    current_time_seconds = round(time.time())
    if pk == 1: 
        eng.start_time = current_time_seconds
        eng.save()
        return redirect('eng-work') 
    
    current_time_seconds_end = current_time_seconds - eng.start_time
    response_time_delta = datetime.timedelta(seconds=round(current_time_seconds_end))
    eng.start_time = 0
    eng.orders_done += 1
    eng.total_response_time += response_time_delta
    eng.average_response_time = eng.total_response_time / eng.orders_done
    current_ticket = Ticket.objects.get(id = pk2)
    current_ticket.response_time = response_time_delta
    current_ticket.status = 'CLOSED'
    current_ticket.equipment.status = 'LIVE'
    current_ticket.save()
    current_ticket.equipment.save()
    eng.save()
    return redirect('eng-work') 

# engineer 
class Add_Department(LoginRequiredMixin, CreateView):
    model = Department
    template_name = 'workflow/add_dep.html'
    form_class = AddDepartmentForm
    context_object_name = 'dep' 
    success_url = reverse_lazy('department-list')

    def form_valid(self, form):
        form.instance.hospital = Engineer.objects.get(id = self.request.user.id).current_hospital
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(Add_Department, self).get_context_data(**kwargs)
        eng = Engineer.objects.get(id = self.request.user.id)
        context['departments'] = Department.objects.filter(hospital = eng.current_hospital)
        context['eng'] = eng
        return context
# eng  > department > edit 
@login_required
def update_department(request, pk):
    dep = Department.objects.get(id = pk)
    if request.method == 'POST':
        d_form = DepartmentUpdateForm(request.POST, instance=dep)
        if d_form.is_valid():
            d_form.save()
            # messages.success(request, f'Account Info Updated!!')
            return redirect('department-list')
              
    d_form = DepartmentUpdateForm(instance=dep)
    equip = dep.equipment_set.all()

    context = {
            'd_form' : d_form,
            'equip' : equip
            }
    return render(request, "workflow/edit_dep.html", context)

@login_required
def update_equipment(request, pk):
    equip = Equipment.objects.get(id = pk)
    deps = equip.hospital.department_set.all()
    if request.method == 'POST':
        e_form = EquipmentUpdateForm(request.POST, instance=equip, deps = deps)
        if e_form.is_valid():
            e_form.save()
            # messages.success(request, f'Account Info Updated!!')
            # return redirect('equipment-details', pk = pk)
            next = request.POST.get('next', request.META.get('HTTP_REFERER'))
            return HttpResponseRedirect(next)              
    e_form = EquipmentUpdateForm(instance=equip, deps = deps)

    context = {
            'e_form' : e_form
            }
    return render(request, "workflow/edit_equip.html", context)

@login_required
def update_edited_equipment(request, pk):
    edited_equip = EditedEquipment.objects.get(id = pk)
    equip = Equipment.objects.get(id = edited_equip.eq_id)
    equip.name = edited_equip.name
    equip.specs = edited_equip.specs
    equip.quantity = edited_equip.quantity
    equip.serial_num = edited_equip.serial_num
    equip.manufacturer = edited_equip.manufacturer
    equip.country = edited_equip.country
    equip.model = edited_equip.model
    equip.risk_level = edited_equip.risk_level
    equip.eq_class = edited_equip.eq_class
    equip.bio_code = edited_equip.bio_code
    equip.med_agent = edited_equip.med_agent
    equip.delivery_date = edited_equip.delivery_date
    equip.warrenty_date = edited_equip.warrenty_date
    equip.department = edited_equip.department
    equip.id = edited_equip.eq_id
    equip.save()
    edited_equip.delete()
    return redirect('welcome')  

class Add_Edited_Equipment(LoginRequiredMixin, CreateView):
    model = EditedEquipment
    template_name = 'workflow/add_edited_equip.html'
    form_class = AddEditedEquipmentForm

    
    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        next = self.request.POST.get('next', self.request.META.get('HTTP_REFERER'))
        if next:
            return next
        else:
            return reverse_lazy('department-list')

    def get_form_kwargs(self):
            kwargs = super(Add_Edited_Equipment, self).get_form_kwargs()
            kwargs.update({'request': self.request, 'pk': self.kwargs['pk']})
            return kwargs
    
    def form_valid(self, form):
        eng = Engineer.objects.get(id = self.request.user.id)
        form.instance.hospital = eng.current_hospital
        form.instance.eq_id = self.kwargs['pk']
        form.instance.eng = eng
        messages.success(self.request, f'A request to Edit Equipment has been sent, waiting for manager approval...')
        return super().form_valid(form)

class Edited_Equipment_Details(LoginRequiredMixin, DetailView):
    model = EditedEquipment
    template_name = 'med/edited_equipment_details.html'

    def get_context_data(self, **kwargs):
        context = super(Edited_Equipment_Details, self).get_context_data(**kwargs)
        context['equipment'] = EditedEquipment.objects.get(id = self.kwargs['pk'])
        return context

class Add_Equipment(LoginRequiredMixin, CreateView):
    model = Equipment
    template_name = 'workflow/add_equip.html'
    form_class = AddEquipmentForm
    # context_object_name = 'equip' 
    # success_url = reverse_lazy('department-list')

    def get_success_url(self):
        next = self.request.POST.get('next', self.request.META.get('HTTP_REFERER'))
        if next:
            return next
        else:
            return reverse_lazy('department-list')
        
    def get_form_kwargs(self):
            kwargs = super(Add_Equipment, self).get_form_kwargs()
            kwargs.update({'request': self.request})
            return kwargs

    def form_valid(self, form):
        form.instance.hospital = Engineer.objects.get(id = self.request.user.id).current_hospital
        if self.request.user.type == 'ENGINEER':
            form.instance.is_approved = False
        messages.success(self.request, f'A request to Add new Equipment has been sent, waiting for manager approval...')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(Add_Equipment, self).get_context_data(**kwargs)
        eng = Engineer.objects.get(id = self.request.user.id)
        context['equipment'] = Equipment.objects.filter(hospital = eng.current_hospital)
        context['eng'] = eng
        return context

@login_required
def approve_added_equipment(request, pk):
    #get equipment
    equipment = Equipment.objects.get(id = pk)
    # approve it
    equipment.is_approved = True
    equipment.save()
    return redirect('welcome')

    
class Add_Equipment_ID(LoginRequiredMixin, CreateView):
    model = Equipment
    template_name = 'workflow/add_equip_id.html'
    form_class = AddEquipmentIDForm
    
    def get_success_url(self):
        next = self.request.POST.get('next', self.request.META.get('HTTP_REFERER'))
        if next:
            return next
        else:
            return reverse_lazy('department-list')

    def form_valid(self, form):
        dep = Department.objects.get(id = self.kwargs['pk'])
        form.instance.department = dep
        form.instance.hospital = dep.hospital
        if self.request.user.type == 'ENGINEER':
            form.instance.is_approved = False
            messages.success(self.request, f'A request to Add new Equipment has been sent, waiting for manager approval...')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(Add_Equipment_ID, self).get_context_data(**kwargs)
        dep = Department.objects.get(id = self.kwargs['pk'])
        context['equipment'] = dep.equipment_set.all()
        return context 








class Add_Procedure(LoginRequiredMixin, CreateView):
    model = Procedure
    template_name = 'workflow/add_procedure.html'
    form_class = AddProcedureForm
    # context_object_name = 'equip' 
    # success_url = reverse_lazy('department-list')

    def get_success_url(self):
        next = self.request.POST.get('next', self.request.META.get('HTTP_REFERER'))
        if next:
            return next
        else:
            return reverse_lazy('department-list')
        
    def get_form_kwargs(self):
            kwargs = super(Add_Procedure, self).get_form_kwargs()
            kwargs.update({'request': self.request})
            return kwargs

    def form_valid(self, form):
        form.instance.hospital = Engineer.objects.get(id = self.request.user.id).current_hospital
        if self.request.user.type == 'ENGINEER':
            form.instance.is_approved = False
        messages.success(self.request, f'A request to Add new Procedure has been sent, waiting for manager approval...')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(Add_Procedure, self).get_context_data(**kwargs)
        eng = Engineer.objects.get(id = self.request.user.id)
        context['procedure'] = Procedure.objects.filter(hospital = eng.current_hospital)
        context['eng'] = eng
        return context

@login_required
def approve_added_procedure(request, pk):
    #get equipment
    procedure = Procedure.objects.get(id = pk)
    # approve it
    procedure.is_approved = True
    procedure.save()
    return redirect('welcome')



