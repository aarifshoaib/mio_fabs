from django.db import models
from client_management.models import AddCompanyModel, NewClientModel
from job_advertisement.models import JobAdvertisementModel
# Create your models here.

class CaptchaIssueModel(models.Model):
    last_update = models.DateTimeField(null=True)
    balance = models.BigIntegerField(null=True)
    error = models.BooleanField(default=False)

class WorkPassModel(models.Model):
    job = models.ForeignKey(JobAdvertisementModel, on_delete=models.SET_NULL, null=True)
    doa = models.DateField(null=True)
    application_no = models.CharField(max_length=300, null=True)
    name = models.CharField(max_length=300, null=True)
    company_name = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    passport_no = models.CharField(max_length=300)
    fin_number = models.CharField(max_length=300, null=True)
    dob = models.DateField(null=True)
    epass_type = models.CharField(max_length=300, null=True)
    status = models.CharField(max_length=300, default='PENDING')
    source = models.CharField(max_length=300, null=True)
    last_update = models.DateTimeField(null=True)
    error = models.BooleanField(default=False)
    not_available = models.BooleanField(default=False)
    apply_copy = models.FileField(upload_to='EPOL_ApplyCopy/', null=True)
    pending_doc = models.FileField(upload_to='Pending_Doc/', null=True)
    rejected_reason = models.FileField(upload_to='EPOL_Reject_Reason/', null=True)

class EmailCredentialModel(models.Model):
    company = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    gmail_id = models.CharField(max_length=300, null=True)
    gmail_app_password = models.CharField(max_length=300, null=True)
    gmail_working_status = models.BooleanField(default=True)

class EmailAttachmentsModel(models.Model):
    attachments = models.FileField(upload_to='EmailAttachments/', null=True)

class EmailTrackerModel(models.Model):
    email_credential = models.ForeignKey(EmailCredentialModel, on_delete=models.CASCADE, null=True)
    from_user = models.CharField(max_length=1000, null=True)
    subject = models.CharField(max_length=1000, null=True)
    receive_date = models.DateTimeField(null=True)
    body = models.TextField(null=True)
    read_status = models.BooleanField(default=True)
    attachments = models.ManyToManyField(EmailAttachmentsModel)

class CPFInvoiceModel(models.Model):
    company = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(null=True)
    pdf_invoice = models.FileField(upload_to='CPF_PDF_Invoice/', null=True)
    csv_invoice = models.FileField(upload_to='CPF_CSV_Invoice/', null=True)
    contribution_date_month = models.DateField(null=True)
    datas = models.JSONField(null=True)

class AfterApprovalTEPModel(models.Model):
    workpass = models.ForeignKey(WorkPassModel, on_delete=models.SET_NULL, null=True)
    upload_ipa = models.FileField(upload_to='UploadIPA/', null=True)
    employee_ind_contact = models.BigIntegerField(null=True)
    employee_sg_contact = models.BigIntegerField(null=True)
    ipa_to_agent = models.CharField(max_length=300, null=True)
    ipa_to_employer = models.CharField(max_length=300, null=True)
    ipa_expiry_date = models.DateField(null=True)
    payment = models.CharField(max_length=300, null=True)
    traval_date = models.DateField(null=True)
    arived_traval_date = models.DateField(null=True)
    extension_due_20_days = models.DateField(null=True)
    new_valid = models.DateField(null=True)
    issue_docs = models.FileField(upload_to='IssueDocs/', null=True)
    issue = models.DateField(null=True)
    card_exp = models.DateField(null=True)
    thump = models.DateField(null=True)
    card_status = models.FileField(upload_to='CardStatus/', null=True)
    ica_upload = models.FileField(upload_to='ICA_File/', null=True)
    notify_acknowledgement = models.FileField(upload_to='notify_acknowledgement/', null=True)
    remarks = models.CharField(max_length=500, null=True)
    driving = models.CharField(max_length=500, null=True)
    other_assignment = models.CharField(max_length=500, null=True)
    is_deleted = models.BooleanField(default=False)

class ApplicationQueueFiles(models.Model):
    attachments = models.FileField(upload_to='ApplicationQueueFiles/', null=True)

class CreateApplicationQueueModel(models.Model):
    from agent_candidate.models import AgentManagementCandidataFormModel
    app_date = models.DateField()
    company = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    passtype = models.CharField(max_length=300)
    employee_ref = models.ForeignKey(AgentManagementCandidataFormModel, on_delete=models.SET_NULL, null=True)
    assigned_by = models.CharField(max_length=300)
    staff = models.CharField(max_length=300)
    status = models.CharField(max_length=300)
    upload_docs = models.ManyToManyField(ApplicationQueueFiles)
    voice_record = models.FileField(upload_to='AppQueueVoiceRecord/', null=True)

class CustomerEntryForm1Model(models.Model):
    ic_number = models.CharField(max_length=500, null=True)
    name = models.CharField(max_length=500, null=True)
    dob = models.DateField(null=True)
    nationality = models.CharField(max_length=500, null=True)
    referby = models.ForeignKey(NewClientModel, on_delete=models.SET_NULL, null=True)
    contact_number = models.BigIntegerField(null=True)
    ic_copy_file = models.FileField(upload_to='CPF_Entry_Form1_IC_Copy/', null=True)

class CustomerEntryForm2Model(models.Model):
    company_name = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    month_year = models.DateField(null=True)
    no_of_fulltime = models.BigIntegerField(null=True)
    no_of_parttime = models.BigIntegerField(null=True)
    declaration = models.CharField(max_length=500)
    draft_upload = models.FileField(upload_to='CPF_Entry_Form2_DraftUpload/', null=True)
