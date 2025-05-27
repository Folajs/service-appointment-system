from django.contrib import admin
from .models import Provider,Customer,Appointment,CustomerDischargeDetails
# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Provider, DoctorAdmin)

class PatientAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, PatientAdmin)

class AppointmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Appointment, AppointmentAdmin)

class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    pass
admin.site.register(CustomerDischargeDetails, PatientDischargeDetailsAdmin)
