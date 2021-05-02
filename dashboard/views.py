from django.shortcuts import render, redirect
from med.models import Manager, Engineer, Doctor
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm


# Create your views here.
def home(request):
    # try : 
        #print(x)   not defind
    #except:
        #print('error')     excute
    try:
        if(request.user.type == 'ENGINEER'):
            eng = Engineer.objects.get(id = request.user.id)
            return render(request, template_name='dashboard/home.html', context={'user' : eng})
        elif(request.user.type == 'DOCTOR'):
            doc = Doctor.objects.get(id = request.user.id)
            return render(request, template_name='dashboard/home.html', context={'user' : doc})
        elif(request.user.type =='MANAGER'):
            man = Manager.objects.get(id = request.user.id)
            return render(request, template_name='dashboard/home.html', context={'user' : man})
    except:
        return render(request, template_name='dashboard/HomePage.html')
    
    
@login_required
def profile(request):
    if(request.user.type == 'ENGINEER'):
        eng = Engineer.objects.get(id = request.user.id)
        return render(request, template_name='dashboard/profile.html', context={'user' : eng})
    elif(request.user.type == 'DOCTOR'):
        doc = Doctor.objects.get(id = request.user.id)
        return render(request, template_name='dashboard/profile.html', context={'user' : doc})
    else:
        return render(request, template_name='dashboard/profile.html')

@login_required
def update_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST,request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            # messages.success(request, f'Account Info Updated!!')
            return redirect('profile')
        else:
            # messages.faliure(request, f'An error has occured!')
            return redirect('profile')
              
    context = {
            'u_form' : UserUpdateForm(instance=request.user),
        }
    return render(request, "dashboard/update_profile.html", context)  