from django.contrib import admin
from django.urls import path
from service import views
from django.contrib.auth.views import LoginView,LogoutView


#-------------FOR ADMIN RELATED URLS
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name=''),
    
    
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

    
    path('adminclick', views.adminclick_view),
    path('providerclick', views.doctorclick_view),
    path('customerclick', views.patientclick_view),

    path('adminsignup', views.admin_signup_view),
    path('providersignup', views.doctor_signup_view,name='providersignup'),
    path('customersignup', views.patient_signup_view),
    
    path('adminlogin', LoginView.as_view(template_name='service/adminlogin.html')),
    path('providerlogin', LoginView.as_view(template_name='service/doctorlogin.html')),
    path('customerlogin', LoginView.as_view(template_name='service/patientlogin.html')),


    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', LogoutView.as_view(template_name='service/index.html'),name='logout'),


    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),

    path('admin-provider', views.admin_doctor_view,name='admin-provider'),
    path('admin-view-provider', views.admin_view_doctor_view,name='admin-view-provider'),
    path('delete-provider-from-service/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-provider-from-service'),
    path('update-provider/<int:pk>', views.update_doctor_view,name='update-provider'),
    path('admin-add-provider', views.admin_add_doctor_view,name='admin-add-provider'),
    path('admin-approve-provider', views.admin_approve_doctor_view,name='admin-approve-provider'),
    path('approve-provider/<int:pk>', views.approve_doctor_view,name='approve-provider'),
    path('reject-provider/<int:pk>', views.reject_doctor_view,name='reject-provider'),
    path('admin-view-provider-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-provider-specialisation'),


    path('admin-customer', views.admin_patient_view,name='admin-customer'),
    path('admin-view-customer', views.admin_view_patient_view,name='admin-view-customer'),
    path('delete-customer-from-service/<int:pk>', views.delete_patient_from_hospital_view,name='delete-customer-from-service'),
    path('update-customer/<int:pk>', views.update_patient_view,name='update-customer'),
    path('admin-add-customer', views.admin_add_patient_view,name='admin-add-customer'),
    path('admin-approve-customer', views.admin_approve_patient_view,name='admin-approve-customer'),
    path('approve-customer/<int:pk>', views.approve_patient_view,name='approve-customer'),
    path('reject-customer/<int:pk>', views.reject_patient_view,name='reject-customer'),
    path('admin-discharge-customer', views.admin_discharge_patient_view,name='admin-discharge-customer'),
    path('discharge-customer/<int:pk>', views.discharge_patient_view,name='discharge-customer'),
    path('download-pdf/<int:pk>', views.download_pdf_view,name='download-pdf'),


    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),
]


#---------FOR PROVIDER RELATED URLS-------------------------------------
urlpatterns +=[
    path('provider-dashboard', views.doctor_dashboard_view,name='provider-dashboard'),

    path('provider-customer', views.doctor_patient_view,name='provider-customer'),
    path('provider-view-customer', views.doctor_view_patient_view,name='provider-view-customer'),
    path('provider-view-discharge-customer',views.doctor_view_discharge_patient_view,name='provider-view-discharge-customer'),

    path('provider-appointment', views.doctor_appointment_view,name='provider-appointment'),
    path('provider-view-appointment', views.doctor_view_appointment_view,name='provider-view-appointment'),
    path('provider-delete-appointment',views.doctor_delete_appointment_view,name='provider-delete-appointment'),
    path('provider-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),
    path('index/', LogoutView.as_view(template_name='service/index.html'),name='index'),
]




#---------FOR CUSTOMER RELATED URLS-------------------------------------
urlpatterns +=[

    path('customer-dashboard', views.patient_dashboard_view,name='customer-dashboard'),
    path('customer-appointment', views.patient_appointment_view,name='customer-appointment'),
    path('customer-book-appointment', views.patient_book_appointment_view,name='customer-book-appointment'),
    path('customer-view-appointment', views.patient_view_appointment_view,name='customer-view-appointment'),
    path('customer-discharge', views.patient_discharge_view,name='customer-discharge'),

]

