from django.db import models
from django.contrib.auth.models import User

class CreateUserModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view_password = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    is_enable = models.BooleanField(default=True)
    def __str__(self) -> str:
        return f"{self.user.username}"

class GenerateOTPModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=100)
    otptime = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.otptime}"

class CreateTitleFolderModel(models.Model):
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=250, null=True)

class FoldersModel(models.Model):
    createdby = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(CreateTitleFolderModel, on_delete=models.CASCADE, null=True)
    folder_name = models.CharField(max_length=250)

class CandidateFormModels(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150)
    phone = models.BigIntegerField(unique=True)
    phone2 = models.BigIntegerField(null=True)
    status = models.BooleanField(default=False)
    asigned_to = models.ForeignKey(CreateUserModel, on_delete=models.CASCADE, null=True)
    folder_id = models.ForeignKey(FoldersModel, on_delete=models.SET_NULL, null=True)

class CountriesListModel(models.Model):
    country_name = models.CharField(max_length=200)

class AgentFormModel(models.Model):
    candidate = models.OneToOneField(CandidateFormModels, on_delete=models.CASCADE, unique=True, null=True)
    candidate_dob = models.DateField(null=True)
    candidate_high_edu = models.TextField(null=True)
    country_experience = models.ManyToManyField(CountriesListModel)
    specify_country_exp = models.BigIntegerField(null=True)
    preferred_country = models.CharField(max_length=150, null=True)
    current_location = models.CharField(max_length=300, null=True)
    job_title = models.TextField(null=True)
    any_physical_challenge = models.BooleanField(default=False)
    specify_physical_challenge = models.TextField(null=True)
    any_relatives = models.BooleanField(default=True)
    specify_any_relatives = models.TextField(null=True)
    select_status = models.BooleanField(default=True)
    specify_select_status = models.TextField(null=True)
    marital_status = models.BooleanField(default=False)
    spouse_highest_edu = models.TextField(null=True)
    spouse_dob = models.DateField(null=True)

class AgentManagementNewAgentModel(models.Model):
    agent_id = models.BigIntegerField(null=True)
    name = models.CharField(max_length=300)
    phone = models.BigIntegerField()
    district = models.CharField(max_length=500, null=True)
    place = models.CharField(max_length=500, null=True)

class AMCandidateUploadPassportModel(models.Model):
    upload_passport = models.FileField(upload_to='AMC_upload_passport/', null=True)

class AMCandidateUploadVideoModel(models.Model):
    upload_video = models.FileField(upload_to='AMC_upload_video/', null=True)

class AMCandidateUploadCertModel(models.Model):
    upload_cert = models.FileField(upload_to='AMC_upload_cert/', null=True)

class AMCandidateUploadResumeModel(models.Model):
    upload_resume = models.FileField(upload_to='AMC_upload_resume/', null=True)

class AMCandidateUploadWorkVideoModel(models.Model):
    upload_work_video = models.FileField(upload_to='AMC_upload_work_video/', null=True)

class AMCandidateUploadInterviewAudioModel(models.Model):
    upload_interview_audio = models.FileField(upload_to='AMC_upload_interview_audio/', null=True)

class AgentManagementCandidataFormModel(models.Model):
    agent = models.ForeignKey(AgentManagementNewAgentModel, on_delete=models.SET_NULL, null=True)
    code_number = models.BigIntegerField(null=True)
    candidate_dob = models.DateField(null=True)
    candidate_high_edu = models.CharField(max_length=500, null=True)
    abroad_exp = models.CharField(max_length=500, null=True)
    sg_pass_detail = models.TextField(null=True)
    applied_pass = models.CharField(max_length=500, null=True)
    specify_note = models.TextField(null=True)
    sat_salary = models.BigIntegerField(null=True)
    selection_command = models.TextField(null=True)
    candidate_name = models.CharField(max_length=500, null=True)
    kyc = models.CharField(max_length=500, null=True)
    current_location = models.CharField(max_length=500, null=True)
    local_exp = models.CharField(max_length=500, null=True)
    applied_position = models.CharField(max_length=500, null=True)
    alternative_position = models.CharField(max_length=500, null=True)
    spouse_dob = models.TextField(null=True)
    any_physical_challenge = models.BooleanField(null=True)
    specify_physical_challenge = models.CharField(max_length=500, null=True)
    any_relatives = models.BooleanField(null=True)
    passport_no = models.CharField(max_length=300, null=True)
    specify_any_relatives = models.CharField(max_length=500, null=True)
    upload_passport = models.ManyToManyField(AMCandidateUploadPassportModel)
    upload_video = models.ManyToManyField(AMCandidateUploadVideoModel)
    upload_cert = models.ManyToManyField(AMCandidateUploadCertModel)
    upload_resume = models.ManyToManyField(AMCandidateUploadResumeModel)
    upload_work_video = models.ManyToManyField(AMCandidateUploadWorkVideoModel)
    upload_interview_audio = models.ManyToManyField(AMCandidateUploadInterviewAudioModel)
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(max_length=100, null=True)

class CandidateAssignCompanyModel(models.Model):
    from client_management.models import AddCompanyModel
    company = models.ForeignKey(AddCompanyModel, on_delete=models.SET_NULL, null=True)
    candidates = models.ManyToManyField(AgentManagementCandidataFormModel)
    unique_id = models.CharField(max_length=300, null=True)

class DashboardModel(models.Model):
    datas = models.JSONField()
