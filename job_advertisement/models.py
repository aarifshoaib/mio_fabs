from django.db import models
from client_management.models import AddCompanyModel,NewClientModel
from django.contrib.auth.models import User


# Create your models here.
class JobAdvertisementModel(models.Model):
    date_of_app = models.DateField()
    maturity_date = models.DateField()
    expiry_date = models.DateField()
    job_code = models.CharField(max_length=300)
    range_field = models.CharField(max_length=300, null=True)
    no_of_vaccancies = models.BigIntegerField(null=True)
    designation = models.CharField(max_length=500)
    comp_name = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    date_of_review = models.DateField(null=True)
    no_of_app = models.BigIntegerField(null=True)
    emp_name = models.CharField(max_length=300, null=True)

class ServerStorageInfoModel(models.Model):
    total_storage = models.CharField(max_length=300, null=True)
    user_storage = models.CharField(max_length=300, null=True)
    total_percent_used = models.CharField(max_length=300, null=True)

class MyTodoModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_date = models.DateField(auto_now=True)
    deadline = models.DateTimeField(null=True)
    task = models.TextField(null=True)
    is_completed = models.BooleanField(default=False)

class RealtimeUserActiveModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=100, null=True)
    active_date = models.DateTimeField()

class StaffMaintenanceModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.JSONField(null=True)

#class EmployeerPersonalNotesModel(models.Model):
  #  user = models.ForeignKey(User, on_delete=models.CASCADE)
   # company = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
   # alert_date = models.DateField()
   # remarks = models.TextField()
   # voice = models.FileField(upload_to='EmployeerPersonalNotesVoices/', null=True)
   # status = models.BooleanField(default=False)

class EmployeerPersonalNotesModel(models.Model):
    id = models.BigAutoField(primary_key=True)  # BigSerial Primary Key
    notes_for = models.CharField(max_length=100, null=True)  # Character varying(100) for notes for
    alert_date = models.DateField()  # Date field for alert
    remarks = models.TextField()  # Text field for remarks
    voice = models.CharField(max_length=100, null=True, blank=True)  # Character varying(100) for voice path
    status = models.BooleanField(default=False)  # Boolean field for status

    # Foreign Key References
    company = models.ForeignKey('client_management.AddCompanyModel', on_delete=models.SET_NULL, null=True)  # Company Master
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User Master
    agent = models.ForeignKey('agent_candidate.AgentManagementNewAgentModel', on_delete=models.SET_NULL, null=True)  # Agent Master
    employer = models.ForeignKey('client_management.NewClientModel', on_delete=models.SET_NULL, null=True)  # Employer Master
    employee = models.ForeignKey('agent_candidate.CandidateFormModels', on_delete=models.SET_NULL, null=True)  # Candidate Master
    contact = models.ForeignKey('job_advertisement.ContactMasterModel', on_delete=models.SET_NULL, null=True)  # Contact Master (New Table)

    # Additional Fields
    contact_name = models.CharField(max_length=200, null=True, blank=True)  # New Contact Name
    contact_number = models.CharField(max_length=100, null=True, blank=True)  # New Contact Number
    others = models.CharField(max_length=300, null=True, blank=True)  # Mandatory if "Others" is selected

    def __str__(self):
        return f"Note by {self.user.username} on {self.alert_date}"
    
class ContactMasterModel(models.Model):
    id= models.BigAutoField(primary_key=True) 
    contact_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contact_name