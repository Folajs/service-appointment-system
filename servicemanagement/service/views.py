from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'service/index.html')

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('index')
    return render(request,'service/index.html')


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'service/adminclick.html')


#for showing signup/login button for provider(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'service/doctorclick.html')


#for showing signup/login button for customer(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'service/patientclick.html')




def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'service/adminsignup.html',{'form':form})




def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor=doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='PROVIDER')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('providerlogin')
    return render(request,'service/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assignedProviderId=request.POST.get('assignedProviderId')
            patient=patient.save()
            my_patient_group = Group.objects.get_or_create(name='CUSTOMER')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'service/patientsignup.html',context=mydict)






#-----------for checking user is provider , customer or admin(by sumit)
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='PROVIDER').exists()
def is_patient(user):
    return user.groups.filter(name='CUSTOMER').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,PROVIDER OR CUSTOMER
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=models.Provider.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('provider-dashboard')
        else:
            return render(request,'service/doctor_wait_for_approval.html')
    elif is_patient(request.user):
        accountapproval=models.Customer.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('customer-dashboard')
        else:
            return render(request,'service/patient_wait_for_approval.html')








#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors=models.Provider.objects.all().order_by('-id')
    patients=models.Customer.objects.all().order_by('-id')
    #for three cards
    doctorcount=models.Provider.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Customer.objects.all().filter(status=False).count()

    patientcount=models.Customer.objects.all().filter(status=True).count()
    pendingpatientcount=models.Customer.objects.all().filter(status=False).count()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'providers':doctors,
    'customers':patients,
    'providercount':doctorcount,
    'pendingprovidercount':pendingdoctorcount,
    'customercount':patientcount,
    'pendingcustomercount':pendingpatientcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'service/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'service/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Provider.objects.all().filter(status=True)
    return render(request,'service/admin_view_doctor.html',{'providers':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Provider.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-provider')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Provider.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'providerForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-provider')
    return render(request,'service/admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'providerForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-provider')
    return render(request,'service/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Provider.objects.all().filter(status=False)
    return render(request,'service/admin_approve_doctor.html',{'providers':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Provider.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-provider'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Provider.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-provider')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Provider.objects.all().filter(status=True)
    return render(request,'service/admin_view_doctor_specialisation.html',{'providers':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'service/admin_patient.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients=models.Customer.objects.all().filter(status=True)
    return render(request,'service/admin_view_patient.html',{'customers':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-customer')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    userForm=forms.PatientUserForm(instance=user)
    patientForm=forms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'customerForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST,instance=user)
        patientForm=forms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.status=True
            patient.assignedProviderId=request.POST.get('assignedPoviderId')
            patient.save()
            return redirect('admin-view-customer')
    return render(request,'service/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'customerForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=True
            patient.assignedProviderId=request.POST.get('assignedProviderId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='CUSTOMER')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'service/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING CUSTOMER BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Customer.objects.all().filter(status=False)
    return render(request,'service/admin_approve_patient.html',{'customers':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Customer.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-customer'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-customer')



#--------------------- FOR DISCHARGING CUSTOMER BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients=models.Customer.objects.all().filter(status=True)
    return render(request,'service/admin_discharge_patient.html',{'customers':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Customer.objects.get(id=pk)
    days=(date.today()-patient.admitDate) #2 days, 0:00:00
    assignedDoctor=models.User.objects.all().filter(id=patient.assignedProviderId)
    d=days.days # only how many day that is 2
    patientDict={
        'customerId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'services':patient.symptoms,
        'admitDate':patient.admitDate,
        'todayDate':date.today(),
        'day':d,
        'assignedProviderName':assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'providerFee':request.POST['providerFee'],
            'productCost' : request.POST['productCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['providerFee'])*int(d))+int(request.POST['productCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.customerId=pk
        pDD.customerName=patient.get_name
        pDD.assignedProviderName=assignedDoctor[0].first_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.services=patient.symptoms
        pDD.admitDate=patient.admitDate
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.productCost=int(request.POST['medicineCost'])
        pDD.providerFee=int(request.POST['providerFee'])*int(d)
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['providerFee'])*int(d))+int(request.POST['productCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'service/patient_final_bill.html',context=patientDict)
    return render(request,'service/patient_generate_bill.html',context=patientDict)



#--------------for discharge customer bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request,pk):
    dischargeDetails=models.CustomerDischargeDetails.objects.all().filter(patientId=pk).order_by('-id')[:1]
    dict={
        'customerName':dischargeDetails[0].customerName,
        'assignedProviderName':dischargeDetails[0].assignedProviderName,
        'address':dischargeDetails[0].address,
        'mobile':dischargeDetails[0].mobile,
        'services':dischargeDetails[0].services,
        'admitDate':dischargeDetails[0].admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'productCost':dischargeDetails[0].productCost,
        'providerFee':dischargeDetails[0].providerFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
    }
    return render_to_pdf('service/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'service/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True)
    return render(request,'service/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            appointment.providerId=request.POST.get('providerId')
            appointment.customerId=request.POST.get('customerId')
            appointment.providerName=models.User.objects.get(id=request.POST.get('providerId')).first_name
            appointment.customerName=models.User.objects.get(id=request.POST.get('customerId')).first_name
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'service/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'service/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PROVIDER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    #for three cards
    patientcount=models.Provider.objects.all().filter(status=True,assignedDoctorId=request.user.id).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,DoctorId=request.user.id).count()
    patientdischarged=models.CustomerDischargeDetails.objects.all().distinct().filter(assignedProviderName=request.user.first_name).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,DoctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.customertId)
    patients=models.Customer.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'customercount':patientcount,
    'appointmentcount':appointmentcount,
    'customerdischarged':patientdischarged,
    'appointments':appointments,
    'provider':models.Provider.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'service/doctor_dashboard.html',context=mydict)



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'provider':models.Provider.objects.get(user_id=request.user.id), #for profile picture of provider in sidebar
    }
    return render(request,'service/doctor_patient.html',context=mydict)



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients=models.Customer.objects.all().filter(status=True,assignedDoctorId=request.user.id)
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    return render(request,'service/doctor_view_patient.html',{'customers':patients,'provider':doctor})



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    dischargedpatients=models.CustomerDischargeDetails.objects.all().distinct().filter(assignedPoviderName=request.user.first_name)
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    return render(request,'service/doctor_view_discharge_patient.html',{'dischargedcustomers':dischargedpatients,'provider':doctor})



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    return render(request,'service/doctor_appointment.html',{'provider':doctor})



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Customer.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'service/doctor_view_appointment.html',{'appointments':appointments,'provider':doctor})



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Customer.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'service/doctor_delete_appointment.html',{'appointments':appointments,'provider':doctor})



@login_required(login_url='providerlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Provider.objects.get(user_id=request.user.id) #for profile picture of provider in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Customer.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'service/doctor_delete_appointment.html',{'appointments':appointments,'provider':doctor})



#---------------------------------------------------------------------------------
#------------------------ PROVIDER RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor=models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict={
    'customer':patient,
    'providerName':doctor.get_name,
    'providerMobile':doctor.mobile,
    'providerAddress':doctor.address,
    'services':patient.services,
    'providerDepartment':doctor.department,
    'admitDate':patient.admitDate,
    }
    return render(request,'service/patient_dashboard.html',context=mydict)



@login_required(login_url='customerlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Customer.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'service/patient_appointment.html',{'customer':patient})



@login_required(login_url='customerlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm=forms.PatientAppointmentForm()
    patient=models.Customer.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'customer':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('providerId'))
            desc=request.POST.get('description')

            doctor=models.Provider.objects.get(user_id=request.POST.get('providerId'))
            
            if doctor.department == 'Carpenters':
                if 'wood' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Provider According To Problem"
                    return render(request,'service/patient_book_appointment.html',{'appointmentForm':appointmentForm,'customer':patient,'message':message})


            if doctor.department == 'Mechanics':
                if 'manchine' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Proider According To Problem"
                    return render(request,'service/patient_book_appointment.html',{'appointmentForm':appointmentForm,'customer':patient,'message':message})

           
            if doctor.department == 'Technicians':
                if 'parts' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Provider According To Problem"
                    return render(request,'service/patient_book_appointment.html',{'appointmentForm':appointmentForm,'customer':patient,'message':message})

            if doctor.department == 'Electricians':
                if 'wire' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Provider According To Problem"
                    return render(request,'service/patient_book_appointment.html',{'appointmentForm':appointmentForm,'customer':patient,'message':message})

            if doctor.department == 'Plumbers':
                if 'water' in desc:
                    pass
                else:
                    print('else')
                    message="Please Choose Provider According To Problem"
                    return render(request,'service/patient_book_appointment.html',{'appointmentForm':appointmentForm,'customer':patient,'message':message})





            appointment=appointmentForm.save(commit=False)
            appointment.providerId=request.POST.get('doctorId')
            appointment.customerId=request.user.id #----user can choose any customer but only their info will be stored
            appointment.providerName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.customerName=request.user.first_name #----user can choose any customer but only their info will be stored
            appointment.status=False
            appointment.save()
        return HttpResponseRedirect('customer-view-appointment')
    return render(request,'service/patient_book_appointment.html',context=mydict)





@login_required(login_url='customerlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient=models.Customer.objects.get(user_id=request.user.id) #for profile picture of customer in sidebar
    appointments=models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request,'service/patient_view_appointment.html',{'appointments':appointments,'customer':patient})



@login_required(login_url='customerlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient=models.Customer.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    dischargeDetails=models.CustomerDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
    patientDict=None
    if dischargeDetails:
        patientDict ={
        'is_discharged':True,
        'customer':patient,
        'customerId':patient.id,
        'customerName':patient.get_name,
        'assignedProviderName':dischargeDetails[0].assignedDoctorName,
        'address':patient.address,
        'mobile':patient.mobile,
        'services':patient.symptoms,
        'admitDate':patient.admitDate,
        'releaseDate':dischargeDetails[0].releaseDate,
        'daySpent':dischargeDetails[0].daySpent,
        'productCost':dischargeDetails[0].productCost,
        'providerFee':dischargeDetails[0].providerFee,
        'OtherCharge':dischargeDetails[0].OtherCharge,
        'total':dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict={
            'is_discharged':False,
            'customer':patient,
            'customerId':request.user.id,
        }
    return render(request,'service/patient_discharge.html',context=patientDict)


#------------------------ CUSTOMER RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'service/contactussuccess.html')
    return render(request, 'service/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


