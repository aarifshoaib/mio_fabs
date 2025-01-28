from django.contrib import admin
from agent_candidate import models

# Register your models here.
admin.site.register(models.CandidateFormModels)
admin.site.register(models.CountriesListModel)
admin.site.register(models.AgentFormModel)
admin.site.register(models.CreateUserModel)