from django.db import models

# Create your models here.
class CandidateForm(models.Model):
    name = models.CharField(max_length=150)
    phone = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

class AgentFormModel(models.Model):
    name = models.CharField(max_length=150)
    phone = models.IntegerField(unique=True)
    experience = models.IntegerField()
    qualification = models.CharField(max_length=150)
    passport_no = models.CharField(max_length=150)
    remarks = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)