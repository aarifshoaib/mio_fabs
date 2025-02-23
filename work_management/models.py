from django.db import models
from agent_candidate.models import CreateUserModel
from django.contrib.auth.models import User
from client_management.models import NewClientModel, AddCompanyModel

# Create your models here.
class AddSubjectModel(models.Model):
    subject = models.TextField(null=True)

class CreateTaskModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(AddSubjectModel, on_delete=models.SET_NULL, null=True)
    employer_name = models.ForeignKey(NewClientModel, on_delete=models.SET_NULL, null=True)
    company_name = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    priority = models.CharField(max_length=300, null=True)
    asigned_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='asigned_by')
    asigned_to = models.ManyToManyField(CreateUserModel)
    description = models.TextField()
    completed_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=300, null=True)
    voice_record = models.FileField(upload_to='VoiceRecord/', null=True)

class AttachmentModel(models.Model):
    task = models.ForeignKey(CreateTaskModel, on_delete=models.CASCADE, null=True)
    attachments = models.FileField(upload_to='CreateTask/')