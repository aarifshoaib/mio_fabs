from django.db import models
from django.contrib.auth.models import User


class CreateUserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view_password = models.CharField(max_length=100, null=True)

class CandidateFormModels(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150)
    phone = models.IntegerField(unique=True)
    phone2 = models.IntegerField(null=True)
    status = models.BooleanField(default=False)
    asigned_to = models.ForeignKey(CreateUserModel, on_delete=models.CASCADE, null=True)

class CountriesListModel(models.Model):
    country_name = models.CharField(max_length=200)

class AgentFormModel(models.Model):
    candidate = models.OneToOneField(CandidateFormModels, on_delete=models.CASCADE, unique=True, null=True)  
    candidate_dob = models.DateField()
    candidate_high_edu = models.TextField()
    country_experience = models.ManyToManyField(CountriesListModel)
    specify_country_exp = models.TextField(null=True)
    preferred_country = models.CharField(max_length=150)
    any_physical_challenge = models.BooleanField(default=False)
    specify_physical_challenge = models.TextField(null=True)
    any_relatives = models.BooleanField(default=True)
    specify_any_relatives = models.TextField(null=True)
    select_status = models.BooleanField(default=True)
    specify_select_status = models.TextField(null=True)
    marital_status = models.BooleanField(default=False)
    spouse_highest_edu = models.TextField(null=True)
    spouse_dob = models.DateField(null=True)
