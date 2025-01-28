from django.contrib import admin
from mom_application import models

# Register your models here.
admin.site.register(models.CPFInvoiceModel)
admin.site.register(models.AfterApprovalTEPModel)