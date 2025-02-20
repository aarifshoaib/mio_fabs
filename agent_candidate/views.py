from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from agent_candidate import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
import django, base64, os, random
from job_advertisement.models import EmployeerPersonalNotesModel
from datetime import datetime, timedelta
from client_management.models import NewClientModel, AddCompanyModel, BuyingSellingModel
from job_advertisement.models import JobAdvertisementModel, ServerStorageInfoModel
from mom_application.models import (EmailTrackerModel, EmailCredentialModel,
                                    WorkPassModel, CreateApplicationQueueModel)

import logging
db_logger = logging.getLogger('db')

# git branch -M main
# git push -u origin main

class Login(View):
    template_name = 'login.html'
    def get(self, request):
        return render(request, self.template_name)

def send_otp_mail(to_addr, html_text):
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart()
    from_gmail = 'myindiaoverseas.me@gmail.com'
    msg['From'] = from_gmail
    msg['To'] = to_addr
    msg['Subject'] = 'My India Overseas Login OTP'

    msg.attach(MIMEText(html_text, 'html'))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.starttls()
    mailServer.login(from_gmail, 'melehveeaxbydoce')
    mailServer.sendmail(from_gmail, to_addr, msg.as_string())
    mailServer.close()

class CheckAuthenticateSecretKeyAPI(View):
    def post(self, request):
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_otp = request.POST.get('otp')
            user_otp = user_otp if user_otp else None
            user = authenticate(username=username, password=password)
            if user is not None:
                chk_user = models.GenerateOTPModel.objects.filter(user=user)
                if chk_user and user_otp is not None: # Otp generated (database) and user input not empty
                    gen_otp = chk_user.first()
                    #chk_secs = ((datetime.today()) - (gen_otp.otptime.replace(tzinfo=None))).seconds
                    chk_secs = 10
                    if chk_secs <= 60:
                        if user_otp == gen_otp.secret_key:
                            login(request, user)
                            gen_otp.delete()
                            response_data = {'status': 'success', 'msg': 'LoggedIn', 'login': True, 'otp_input': False}
                        else:
                            response_data = {'status': 'error', 'msg': 'Invalid OTP. Try Again', 'login': False, 'otp_input': True}
                    else:
                        gen_otp.delete()
                        response_data = {'status': 'error', 'msg': 'Invalid OTP. TimeOut, Try Again', 'login': False, 'otp_input': False}
                elif not chk_user and user_otp is None: # otp not generated and otp input empty
                    secret_key=random.randint(100000, 999999)
                    gen_otp = models.GenerateOTPModel(user=user, secret_key=secret_key)
                    gen_otp.save()
                    otp_html_template = f'''
                            <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
                            <div style="margin:50px auto;width:70%;padding:20px 0">
                                <div style="border-bottom:1px solid #eee">
                                <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">My India Overseas</a>
                                </div>
                                <p style="font-size:1.1em">Hi,</p>
                                <p>Use the following OTP to complete your Login procedures. OTP is valid for 1 minutes</p>
                                <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{secret_key}</h2>
                                <p style="font-size:0.9em;">Regards,<br />My India Overseas</p>
                                <hr style="border:none;border-top:1px solid #eee" />

                            </div>
                            </div>
                            '''
                    send_otp_mail(user.email, otp_html_template)
                    response_data = {'status': 'success', 'msg': 'Enter OTP', 'login': False, 'otp_input': True}
                elif chk_user and user_otp is None:
                    gen_otp = chk_user.first()
                    gen_otp.delete()

                    secret_key = random.randint(100000, 999999)
                    gen_otp = models.GenerateOTPModel(user=user, secret_key=secret_key)
                    gen_otp.save()

                    otp_html_template = f'''
                            <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
                            <div style="margin:50px auto;width:70%;padding:20px 0">
                                <div style="border-bottom:1px solid #eee">
                                <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">My India Overseas</a>
                                </div>
                                <p style="font-size:1.1em">Hi,</p>
                                <p>Use the following OTP to complete your Login procedures. OTP is valid for 1 minutes</p>
                                <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{secret_key}</h2>
                                <p style="font-size:0.9em;">Regards,<br />My India Overseas</p>
                                <hr style="border:none;border-top:1px solid #eee" />

                            </div>
                            </div>
                            '''
                    send_otp_mail(user.email, otp_html_template)
                    response_data = {'status': 'success', 'msg': 'Enter OTP', 'login': False, 'otp_input': True}
                else:
                    response_data = {'status': 'error', 'msg': 'Something Wrong. Retry', 'login': False, 'otp_input': False}
            else:
                response_data = {'status': 'error', 'msg': 'Username/password Incorrect', 'login': False, 'otp_input': False}
        except Exception as e:
            response_data = {'status': 'error', 'msg': f'Error: {e}', 'login': False, 'otp_input': False}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
# class Dashboard(View):
#     template_name = 'admin-dashboard.html'

#     def get(self, request):
#         today = datetime.today().date()
#         app_queue = CreateApplicationQueueModel.objects.all().order_by('-app_date')[:2]

#         try:
#             server_info = ServerStorageInfoModel.objects.first()
#         except:
#             server_info = None

#         # Fetching the latest notes for the logged-in user
#         try:
#             user = request.user
#             latest_notes = EmployeerPersonalNotesModel.objects.filter(user=user).order_by('-alert_date')[:5]  # Show latest 5 notes
#         except Exception as e:
#             latest_notes = []

#         # Prepare the context data
#         datas = {
#             'today': today,
#             'app_queue': app_queue,
#             'server_info': server_info,
#             'latest_notes': latest_notes
#         }

#         # Update context with dashboard-specific data
#         d = models.DashboardModel.objects.last()
#         datas.update(d.datas)

#         return render(request, self.template_name, context=datas)
class Dashboard(View):
    template_name = 'admin-dashboard.html'

    def get(self, request):
        today = datetime.today().date()
        app_queue = CreateApplicationQueueModel.objects.all().order_by('-app_date')[:2]

        try:
            server_info = ServerStorageInfoModel.objects.first()
        except:
            server_info = None

        # Fetch notes where alert_date matches today's date
        try:
            user = request.user
            today_notes = EmployeerPersonalNotesModel.objects.filter(user=user, alert_date=today)
            notes = EmployeerPersonalNotesModel.objects.filter(user=user).order_by('-id')  # Fetch all notes for the user
            empnotescnt = notes.count()
        except Exception as e:
            today_notes = []
            notes = []  # Handle if there's an issue fetching the notes
            empnotescnt = 0

        # Prepare the context data
        datas = {
            'today': today,
            'app_queue': app_queue,
            'server_info': server_info,
            'today_notes': today_notes , # Updated to use only today's notes
            'notes': notes,  # Add all notes to the context
            'empnotescnt': empnotescnt,
        }

        # Update context with dashboard-specific data
        d = models.DashboardModel.objects.last()
        datas.update(d.datas)

        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required(['agent_candidate.view_candidateformmodels',
            'agent_candidate.add_candidateformmodels',
            'agent_candidate.change_candidateformmodels'], raise_exception=True), name='dispatch')
class CandidateForm(View):
    template_name = 'candidate-form.html'
    def get(self, request, id=None):
        agents = models.CreateUserModel.objects.filter(user__groups__name='Agent')
        candidate_detail = {'agents': agents}
        if id is not None:
            candidate = models.CandidateFormModels.objects.get(id=id)
            candidate_detail['candidate'] = candidate
        return render(request, self.template_name, context=candidate_detail)

    def post(self, request, id=None):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        phone2 = request.POST.get('phone2') if request.POST.get('phone2') else None
        asigned_to = request.POST.get('asigned_to')

        user = User.objects.get(username=asigned_to)
        asigned_to = models.CreateUserModel.objects.get(user=user)

        if id:
            try:
                reg_form = models.CandidateFormModels.objects.get(id=id)
                reg_form.name = name
                reg_form.phone = phone
                reg_form.phone2 = phone2
                reg_form.asigned_to = asigned_to
                reg_form.save()
                messages.success(request, 'Candidate Updated Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
            except Exception as e:
                messages.info(request, f'Error: {e}')
            return redirect('/agent-candidate/candidate-details')
        else:
            try:
                reg_form = models.CandidateFormModels(name=name, phone=phone, phone2=phone2, asigned_to=asigned_to)
                reg_form.save()
                messages.success(request, 'Candidate Created Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
            except Exception as e:
                messages.info(request, f'Error: {e}')
        return redirect('/agent-candidate/candidate-form')

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required('agent_candidate.view_candidateformmodels', raise_exception=True), name='dispatch')
class CandidateDetails(View):
    template_name = 'candidate-details.html'

    def get(self, request, folder_id=None):
        if request.user.is_staff:
            if folder_id is None:
                candidates = models.CandidateFormModels.objects.all()
            else:
                folder = models.FoldersModel.objects.get(id=folder_id)
                candidates = models.CandidateFormModels.objects.filter(folder_id=folder)
        elif request.user.groups.all().first().name in ['Admin', 'HR']:
            if folder_id is None:
                candidates = models.CandidateFormModels.objects.all()
            else:
                folder = models.FoldersModel.objects.get(id=folder_id)
                candidates = models.CandidateFormModels.objects.filter(folder_id=folder)
        else:
            user = request.user.username
            user = User.objects.get(username=user)
            createuser = models.CreateUserModel.objects.get(user=user)
            candidates = models.CandidateFormModels.objects.filter(asigned_to=createuser)

            if folder_id is not None:
                folder = models.FoldersModel.objects.get(id=folder_id)
                candidates = models.CandidateFormModels.objects.filter(folder_id=folder)

        get_url = request.get_full_path()

        if 'params' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        try:
            exp_syb, exp = request.GET.get('exp_syb'), int(str(request.GET.get('exp')))
        except:
            exp, exp_syb = None, None

        try:
            age_syb, age = request.GET.get('age_syb'), int(str(request.GET.get('age')))
        except:
            age, age_syb = None, None

        try:
            status = int(str(request.GET.get('status')))
        except:
            status = None

        job_title = request.GET.get('job-title') if request.GET.get('job-title') else None
        location = request.GET.get('location') if request.GET.get('location') else None

        if exp is not None:
            if exp_syb == '=':
                agent = models.AgentFormModel.objects.filter(specify_country_exp=exp).values_list('candidate', flat=True)
            elif exp_syb == '>=':
                agent = models.AgentFormModel.objects.filter(specify_country_exp__gte=exp).values_list('candidate', flat=True)
            elif exp_syb == '<=':
                agent = models.AgentFormModel.objects.filter(specify_country_exp__lte=exp).values_list('candidate', flat=True)
            candidates = candidates.filter(id__in=agent)

        if age is not None:
            if age_syb == '=':
                agent = models.AgentFormModel.objects.filter(candidate_dob__year=age).values_list('candidate', flat=True)
            elif age_syb == '>=':
                agent = models.AgentFormModel.objects.filter(candidate_dob__year__gte=age).values_list('candidate', flat=True)
            elif age_syb == '<=':
                agent = models.AgentFormModel.objects.filter(candidate_dob__year__lte=age).values_list('candidate', flat=True)
            candidates = candidates.filter(id__in=agent)

        if job_title is not None:
            agent = models.AgentFormModel.objects.filter(job_title__icontains=job_title).values_list('candidate', flat=True)
            if agent:
                candidates = candidates.filter(id__in=agent)
            else:
                candidates = candidates.filter(name__icontains=job_title)


        if location is not None:
            agent = models.AgentFormModel.objects.filter(current_location__icontains=location).values_list('candidate', flat=True)
            candidates = candidates.filter(id__in=agent)

        if status is not None:
            if status:
                candidates = candidates.filter(status=True)
            else:
                candidates = candidates.filter(status=False)

        candidate_page = Paginator(candidates, 15)
        page_number = request.GET.get('page')

        try:
            candidate_page = candidate_page.get_page(page_number)
        except PageNotAnInteger:
            candidate_page = candidate_page.page(1)
        except EmptyPage:
            candidate_page = candidate_page.page(candidate_page.num_pages)


        datas = {
                    'candidate_page': candidate_page,
                    'candidate_count': candidates.count(),
                    'completed': candidates.filter(status=True).count(),
                    'pending': candidates.filter(status=False).count(),
                    'countries': models.CountriesListModel.objects.all(),
                    'current_url': current_url,
                    'folders': models.FoldersModel.objects.all(),
                    'folder_id': folder_id,
                    'params': [job_title if job_title else '', age_syb, age, exp_syb, exp, location if location else '', status],
                    'symbols': ['=', '>=', '<='],
                    'back': base64.urlsafe_b64encode(f"{request.get_full_path()}".encode()).decode(),
                }

        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required('agent_candidate.delete_candidateformmodels', raise_exception=True), name='dispatch')
class CandidateDelete(View):
    def get(self, request, folder_id, id):
        if folder_id == 0:
            candidate = models.CandidateFormModels.objects.get(id=id)
            candidate.delete()
            return redirect('/agent-candidate/candidate-details')
        else:
            candidate = models.CandidateFormModels.objects.get(id=id)
            candidate.folder_id = None
            candidate.save()
            return redirect(f'/agent-candidate/candidate-details/{folder_id}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class FoldersLinkView(View):
    def get(self, request, id, page):
        candidate = models.CandidateFormModels.objects.get(id=id)
        folder_name = request.GET.get('folder-name')
        folder = models.FoldersModel.objects.get(folder_name=folder_name)

        candidate.folder_id = folder
        candidate.save()

        messages.info(request, f"{candidate.name} Moved To {folder_name}")
        if page == 1:
            return redirect('/agent-candidate/candidate-details')
        return redirect(f'/agent-candidate/candidate-details?page={page}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateFolderView(View):
    template_name = 'create-folder.html'
    def get(self, request, title_id, id=None):

        if id is None:
            user = User.objects.get(username=request.user.username)
            title = models.CreateTitleFolderModel.objects.get(id=title_id)
            folders = models.FoldersModel.objects.filter(createdby=user, title=title)
            datas = {
                        'create_folders': folders,
                }
        else:
            try:
                folder = models.FoldersModel.objects.get(id=id)
                datas = {
                        'create_folder': folder,
                        'edit': id,
                }
            except Exception as e:
                messages.info(request, f"Error: {e}")
                datas = {}

        return render(request, self.template_name, context=datas)

    def post(self, request, title_id, id=None):
        folder_name = request.POST.get('folder-name')
        user = User.objects.get(username=request.user.username)
        title_folder = models.CreateTitleFolderModel.objects.get(id=title_id)

        if id is None:
            try:

                folder = models.FoldersModel(createdby=user, title=title_folder, folder_name=folder_name)
                folder.save()
                messages.info(request, f"{folder_name} New Folder Created")
            except Exception as e:
                messages.info(request, f"Error: {e}")
        else:
            try:
                folder = models.FoldersModel.objects.get(id=id)
                folder.createdby = user
                folder.title = title_folder
                folder.folder_name = folder_name
                folder.save()
                messages.info(request, f"{folder_name} Updated..")
            except Exception as e:
                messages.info(request, f"Error: {e}")

        return redirect(f'/agent-candidate/create-folder/{title_id}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteFolderView(View):
    def get(self, request, title_id, id):
        try:
            folder = models.FoldersModel.objects.get(id=id)
            folder.delete()
            messages.info(request, f"{folder.folder_name} Deleted..")
        except Exception as e:
            messages.info(request, f"Error: {e}")
        return redirect(f'/agent-candidate/create-folder/{title_id}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateTitleFolderView(View):
    template_name = 'create-title-folder.html'
    def get(self, request, id=None):
        if id is None:
            user = User.objects.get(username=request.user.username)
            # folders = models.CreateTitleFolderModel.objects.filter(createdby=user)
            folders = models.CreateTitleFolderModel.objects.all()
            datas = {
                        'create_folders': folders,
                }
        else:
            try:
                folder = models.CreateTitleFolderModel.objects.get(id=id)
                datas = {
                        'create_folder': folder,
                        'edit': id,
                }
            except Exception as e:
                messages.info(request, f"Error: {e}")
                datas = {}

        return render(request, self.template_name, context=datas)

    def post(self, request, id=None):
        folder_name = request.POST.get('folder-name')
        user = User.objects.get(username=request.user.username)

        if id is None:
            try:
                folder = models.CreateTitleFolderModel(createdby=user, title=folder_name)
                folder.save()
                messages.info(request, f"{folder_name} New Folder Created")
            except Exception as e:
                messages.info(request, f"Error: {e}")
        else:
            try:
                folder = models.CreateTitleFolderModel.objects.get(id=id)
                folder.createdby = user
                folder.title = folder_name
                folder.save()
                messages.info(request, f"{folder_name} Updated..")
            except Exception as e:
                messages.info(request, f"Error: {e}")

        return redirect('/agent-candidate/create-title-folder')

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteTitleFolderView(View):
    def get(self, request, id):
        try:
            folder = models.CreateTitleFolderModel.objects.get(id=id)
            folder.delete()
            messages.info(request, f"{folder.title} Deleted..")
        except Exception as e:
            messages.info(request, f"Error: {e}")
        return redirect('/agent-candidate/create-title-folder')

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("/")

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required(['agent_candidate.add_agentformmodel',
            'agent_candidate.view_agentformmodel',
            'agent_candidate.change_agentformmodel'], raise_exception=True), name='dispatch')
class AgentForm(View):
    template_name = 'agent.html'
    def get(self, request, id, back=None):
        countries = models.CountriesListModel.objects.all()
        candidate_detail = {'countries': countries}
        if back is not None:
            candidate_detail['back'] = base64.urlsafe_b64decode(back.encode()).decode()
        else:
            candidate_detail['back'] = '/agent-candidate/candidate-details'

        if id is not None:

            candidate = models.CandidateFormModels.objects.get(id=id)
            candidate_detail['candidate'] = candidate

            agent = models.AgentFormModel.objects.filter(candidate=candidate)
            if agent:
                if agent.first().candidate_dob:
                    candidate_detail['candidate_dob'] = agent.first().candidate_dob.strftime('%d/%m/%Y')
                if agent.first().spouse_dob:
                    candidate_detail['spouse_dob'] = agent.first().spouse_dob.strftime('%d/%m/%Y')
                candidate_detail['countries_list'] = [i.country_name for i in agent.first().country_experience.all()]
                candidate_detail['agent'] = agent.first()

        return render(request, self.template_name, context=candidate_detail)

    def post(self, request, id, back=None):
        if back is not None:
            back = back.encode().decode()
        else:
            back = base64.urlsafe_b64encode('/agent-candidate/candidate-details'.encode()).decode()

        username = request.user
        candidate_name = request.POST.get('candidate_name')
        phone = request.POST.get('phone')
        candidate_dob = request.POST.get('candidate_dob')
        phone2 = request.POST.get('phone2')
        candidate_high_edu = request.POST.get('candidate_high_edu')
        country_experience = request.POST.getlist('country_experience')
        specify_country_exp = request.POST.get('specify_country_exp')
        preferred_country = request.POST.get('preferred_country')
        any_physical_challenge = request.POST.get('any_physical_challenge')
        specify_physical_challenge = request.POST.get('specify_physical_challenge')
        any_relatives = request.POST.get('any_relatives')
        specify_any_relatives = request.POST.get('specify_any_relatives')
        select_status = request.POST.get('select_status')
        specify_select_status = request.POST.get('specify_select_status')
        marital_status = request.POST.get('marital_status')
        spouse_highest_edu = request.POST.get('spouse_highest_edu')
        spouse_dob = request.POST.get('spouse_dob')
        current_location = request.POST.get('current_location')
        job_title = request.POST.get('job_title')

        user = User.objects.get(username=username)

        print(candidate_dob)

        try:
            specify_country_exp = int(request.POST.get('specify_country_exp'))
        except:
            specify_country_exp = None

        try:
            phone = int(request.POST.get('phone'))
        except:
            phone = None

        try:
            phone2 = int(request.POST.get('phone2'))
        except:
            phone2 = None

        try:
            candidate_dob = datetime.strptime(candidate_dob, '%d/%m/%Y').date()
        except:
            candidate_dob = None

        try:
            spouse_dob = datetime.strptime(spouse_dob, '%d/%m/%Y').date()
        except:
            spouse_dob = None

        candidate = models.CandidateFormModels.objects.get(id=id)
        candidate.user = user
        candidate.name = candidate_name
        candidate.phone = phone
        candidate.phone2 = phone2 if phone2 else None
        candidate.status = True
        candidate.save()

        if any_physical_challenge == 'y':
            any_physical_challenge = True
        else:
            any_physical_challenge = False
            specify_physical_challenge = ''

        if any_relatives == 'y':
            any_relatives = True
        else:
            any_relatives = False
            specify_any_relatives = ''

        if marital_status == 'y':
            marital_status = True
        else:
            marital_status = False
            spouse_highest_edu, spouse_dob = '', None

        if select_status == 'y':
            select_status = True
            specify_select_status = ''
        else:
            select_status = False

        if not models.AgentFormModel.objects.filter(candidate=candidate):
            try:
                agent = models.AgentFormModel(candidate=candidate,candidate_dob=candidate_dob,candidate_high_edu=candidate_high_edu,
                specify_country_exp=specify_country_exp,preferred_country=preferred_country,any_physical_challenge=any_physical_challenge,
                specify_physical_challenge=specify_physical_challenge,any_relatives=any_relatives,specify_any_relatives=specify_any_relatives,
                select_status=select_status,specify_select_status=specify_select_status,marital_status=marital_status,
                spouse_highest_edu=spouse_highest_edu,spouse_dob=spouse_dob, current_location=current_location, job_title=job_title)
                agent.save()

                for cntry in country_experience:
                    country = models.CountriesListModel.objects.get(country_name=cntry)
                    agent.country_experience.add(country)

                messages.success(request, 'Candidate Details Updated Successfully.')
            except Exception as e:
                messages.info(request, f'{e}')

            return redirect(f'/agent-candidate/agent-form/{id}/{back}')
        else:
            try:
                agent = models.AgentFormModel.objects.get(candidate=candidate)
                agent.candidate=candidate
                agent.candidate_dob=candidate_dob
                agent.candidate_high_edu=candidate_high_edu
                agent.specify_country_exp=specify_country_exp
                agent.preferred_country=preferred_country
                agent.any_physical_challenge=any_physical_challenge
                agent.specify_physical_challenge=specify_physical_challenge
                agent.any_relatives=any_relatives
                agent.specify_any_relatives=specify_any_relatives
                agent.select_status=select_status
                agent.specify_select_status=specify_select_status
                agent.marital_status=marital_status
                agent.spouse_highest_edu=spouse_highest_edu
                agent.spouse_dob=spouse_dob
                agent.current_location = current_location
                agent.job_title = job_title
                agent.save()

                agent.country_experience.clear()
                for cntry in country_experience:
                    country = models.CountriesListModel.objects.get(country_name=cntry)
                    agent.country_experience.add(country)
                messages.success(request, 'Candidate Edited Successfully.')
            except Exception as e:
                messages.info(request, e)

            return redirect(f'/agent-candidate/agent-form/{id}/{back}')

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required(['agent_candidate.add_createusermodel',
            'agent_candidate.view_createusermodel',
            'agent_candidate.change_createusermodel'], raise_exception=True), name='dispatch')
class CreateUsers(View):
    template_name = 'create-user.html'
    def get(self, request, id=None):
        agents_datas = {'roles': [ grup.name for grup in Group.objects.all() ]}
        if id is not None:
            agents = models.CreateUserModel.objects.get(id=id)
            agents_datas['user'] = agents
        else:
            agents = models.CreateUserModel.objects.all()
            agents_datas['agents'] = agents
        return render(request, self.template_name, context=agents_datas)

    def post(self, request, id=None):
        user_role = request.POST.get('role')
        user_name = request.POST.get('user-name')
        user_email = request.POST.get('user-email')
        user_phone = request.POST.get('user-phone')
        user_password = request.POST.get('password1')
        user_confirm_password = request.POST.get('password2')

        if id is not None:
            if user_password == user_confirm_password:
                try:
                    agent_user = models.CreateUserModel.objects.get(id=id)

                    user = User.objects.get(username=agent_user.user.username)
                    user.username = user_name
                    user.email = user_email
                    user.set_password(user_password)
                    user.groups.clear()
                    user.save()

                    group_mod = Group.objects.get(name=user_role)
                    group_mod.user_set.add(user)

                    a_user = User.objects.get(username=user_name)

                    agent_user.user = a_user
                    agent_user.view_password = user_password
                    agent_user.phone = user_phone
                    agent_user.save()

                    messages.success(request, f'{user_name} - Edited.')
                except django.db.utils.IntegrityError:
                    messages.info(request, f'"{user_name}" username. Already Exists!!')
                except Exception as e:
                    messages.info(request, e)
            else:
                messages.info(request, 'Password Mismatch!!')

        else:
            if user_password == user_confirm_password:
                try:
                    user = User.objects.create_user(username=user_name, email=user_email, password=user_password)
                    user.save()

                    group_mod = Group.objects.get(name=user_role)
                    group_mod.user_set.add(user)

                    a_user = User.objects.get(username=user_name)

                    agent_user = models.CreateUserModel(user=a_user, view_password=user_password,
                                                            phone=user_phone)
                    agent_user.save()
                    messages.success(request, f'{user_name} - Created.')
                except django.db.utils.IntegrityError:
                    messages.info(request, f'"{user_name}" username. Already Exists!!')
                except Exception as e:
                    messages.info(request, e)
            else:
                messages.info(request, 'Password Mismatch!!')

        return redirect('/agent-candidate/create-user')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateUserDelete(View):
    def get(self, request, id):
        user = models.CreateUserModel.objects.get(id=id)
        u = User.objects.get(id=user.user.id)
        u.delete()
        user.delete()
        return redirect('/agent-candidate/create-user')


# Agent Management Part ------------------------------------------------------------------------
def url_encode_func(url, encode=True):
    if encode:
        return base64.urlsafe_b64encode(url.encode()).decode()
    return base64.urlsafe_b64decode(url.encode()).decode()

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementNewAgentView(View):
    template_name='agent-management-new-agent.html'
    def get_agent_id(self):
        agent = models.AgentManagementNewAgentModel.objects.all()
        if agent.count() == 0:
            return 0
        return agent.last().agent_id + 1

    def get(self, request, id=None, return_url=None):
        districts = ['Ariyalur (அரியலூர்)', 'Chengalpattu (செங்கல்பட்டு)', 'Chennai (சென்னை)',
                     'Coimbatore (கோயம்புத்தூர்)', 'Cuddalore (கடலூர்)', 'Dharmapuri (தர்மபுரி)',
                     'Dindigul (திண்டுக்கல்)', 'Erode (ஈரோடு)', 'Kallakurichi (கல்லக்குறிச்சி)',
                     'Kanchipuram (காஞ்சிபுரம்)', 'Kanniyakumari (கன்னியாகுமரி)', 'Karur (கரூர்)',
                     'Krishnagiri (கிருஷ்ணகிரி)', 'Madurai (மதுரை)', 'Mayiladuthurai (மயிலாடுதுறை)',
                     'Nagapattinam (நாகப்பட்டினம்)', 'Namakkal (நாமக்கல்)', 'Nilgiris (நீலகிரி)',
                     'Perambalur (பெரம்பலூர்)', 'Pudukkottai (புதுக்கோட்டை)',
                     'Ramanathapuram (ராமநாதபுரம்)', 'Ranipet (ராணிப்பேட்டை)',
                     'Salem (சேலம்)', 'Sivagangai (சிவகங்கை)', 'Tenkasi (தென்காசி)',
                     'Thanjavur (தஞ்சாவூர்)', 'Theni (தேனி)', 'Thoothukudi (தூத்துக்குடி)',
                     'Tiruchirappalli (திருச்சிராப்பள்ளி)', 'Tirunelveli (திருநெல்வேலி)',
                     'Tirupathur (திருப்பத்தூர்)', 'Tiruppur (திருப்பூர்)', 'Tiruvallur (திருவள்ளூர்)',
                     'Tiruvannamalai (திருவண்ணாமலை)', 'Tiruvarur (திருவாரூர்)', 'Vellore (வேலூர்)',
                     'Viluppuram (விழுப்புரம்)', 'Virudhunagar (விருதுநகர்)', 'Not Applicable']
        datas = {'districts': districts}
        try:
            if id:
                agent = models.AgentManagementNewAgentModel.objects.get(id=id)
                datas['agent'] = agent
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return render(request, self.template_name, context=datas)

    def post(self, request, id=None, return_url=None):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        district = request.POST.get('district')
        place = request.POST.get('place')
        if id:
            try:
                new_agent = models.AgentManagementNewAgentModel.objects.get(id=id)
                new_agent.name = name
                new_agent.phone = phone
                new_agent.district = district
                new_agent.place = place
                new_agent.save()
                messages.success(request, f'Agent "{name}" Updated.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            try:
                agent_id = self.get_agent_id()

                new_agent = models.AgentManagementNewAgentModel(agent_id=agent_id, name=name,
                                phone=phone, district=district, place=place)
                new_agent.save()
                messages.success(request, f'New Agent "{name}" Added.')
            except Exception as e:
                messages.error(request, f'Error: {e}')

        if return_url:
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                pass
        return redirect('/agent-candidate/agent-management-new-agent')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementAgentListView(View):
    template_name='agent-management-agent-list.html'
    def col2num(self, col):
        import string
        num = 0
        for c in col:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        return num-1

    def get(self, request):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        if keyword:
            try:
                if 'id=' in keyword:
                    try:
                        agent_id = self.col2num(keyword.split('=')[1])
                        agents = models.AgentManagementNewAgentModel.objects.filter(agent_id=agent_id)
                    except:
                        agents = models.AgentManagementNewAgentModel.objects.all()
                else:
                    agents = models.AgentManagementNewAgentModel.objects.filter(Q(name__icontains=keyword)|
                                        Q(phone__icontains=keyword)|Q(district__icontains=keyword)|
                                        Q(place__icontains=keyword))
            except:
                agents = models.AgentManagementNewAgentModel.objects.all()
        else:
            agents = models.AgentManagementNewAgentModel.objects.all()
        agents_page = Paginator(agents.order_by('agent_id'), 25)
        page_number = request.GET.get('page')
        try:
            agents_page = agents_page.get_page(page_number)
        except PageNotAnInteger:
            agents_page = agents_page.page(1)
        except EmptyPage:
            agents_page = agents_page.page(agents_page.num_pages)
        datas = {
            'agents': agents_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': agents.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Agent List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementAgentDeleteView(View):
    def get(sef, request, id, return_url):
        try:
            agent = models.AgentManagementNewAgentModel.objects.get(id=id)
            name = agent.name
            agent.delete()
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {name} Agent')
            messages.success(request, f'Agent "{name}" Deleted!')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        if return_url:
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                pass
        return redirect('/agent-candidate/agent-management-agent-list')

def get_agent_code_number(candidates):
    if candidates:
        cand = candidates.order_by('code_number').last()
        return cand.code_number + 1
    return 1

def candidateform_api(request, id=None, return_url=None):
    if request.method == 'POST':
        agent_name=request.POST.get('agent-name')
        candidate_dob=request.POST.get('candidate_dob')
        candidate_high_edu = request.POST.get('candidate_high_edu')
        abroad_exp = request.POST.get('abroad-exp')
        sg_pass_detail = request.POST.get('sg-pass-detail')
        applied_pass = request.POST.get('applied-pass')
        specify_note = request.POST.get('specify-note')
        # sat_salary = request.POST.get('sat-salary')
        selection_command = request.POST.get('selection-command')
        candidate_name = request.POST.get('candidate-name')
        kyc = request.POST.get('kyc')
        passport_no = request.POST.get('passport_no')
        current_location = request.POST.get('current-location')
        local_exp = request.POST.get('local-exp')
        applied_position = request.POST.get('applied-position')
        alternative_position = request.POST.get('alternative-position')
        spouse_dob = request.POST.get('spouse-dob')
        any_physical_challenge = request.POST.get('any_physical_challenge')
        specify_physical_challenge = request.POST.get('specify_physical_challenge')
        any_relatives = request.POST.get('any_relatives')
        specify_any_relatives = request.POST.get('specify_any_relatives')

        # Files
        upload_passport = request.FILES.getlist('upload-passport')
        upload_video = request.FILES.getlist('upload-video')
        upload_cert = request.FILES.getlist('upload-cert')
        upload_resume = request.FILES.getlist('upload-resume')
        upload_work_video = request.FILES.getlist('upload-work-video')
        upload_interview_audio = request.FILES.getlist('upload-interview-audio')

        if id:
            try:
                agent = models.AgentManagementNewAgentModel.objects.get(id=agent_name)
                try:
                    candidate_dob = datetime.strptime(candidate_dob, '%d/%m/%Y')
                except:
                    candidate_dob = None
                any_physical_challenge = True if any_physical_challenge == 'y' else False
                any_relatives = True if any_relatives == 'y' else False
                # sat_salary = sat_salary if sat_salary else None
                update_candidate = models.AgentManagementCandidataFormModel.objects.get(id=id)
                update_candidate.agent=agent
                update_candidate.candidate_dob=candidate_dob
                update_candidate.candidate_high_edu=candidate_high_edu
                update_candidate.abroad_exp=abroad_exp
                update_candidate.sg_pass_detail=sg_pass_detail
                update_candidate.applied_pass=applied_pass
                update_candidate.specify_note=specify_note
                # update_candidate.sat_salary=sat_salary
                update_candidate.selection_command=selection_command
                update_candidate.candidate_name=candidate_name
                update_candidate.kyc=kyc
                update_candidate.passport_no=passport_no
                update_candidate.current_location=current_location
                update_candidate.local_exp=local_exp
                update_candidate.applied_position=applied_position
                update_candidate.alternative_position=alternative_position
                update_candidate.spouse_dob=spouse_dob
                update_candidate.any_physical_challenge=any_physical_challenge
                update_candidate.specify_physical_challenge=specify_physical_challenge
                update_candidate.any_relatives=any_relatives
                update_candidate.specify_any_relatives=specify_any_relatives
                if upload_passport:
                    for file in upload_passport:
                        upload_f = models.AMCandidateUploadPassportModel(upload_passport=file)
                        upload_f.save()
                        update_candidate.upload_passport.add(upload_f)
                if upload_video:
                    for file in upload_video:
                        upload_f = models.AMCandidateUploadVideoModel(upload_video=file)
                        upload_f.save()
                        update_candidate.upload_video.add(upload_f)
                if upload_cert:
                    for file in upload_cert:
                        upload_f = models.AMCandidateUploadCertModel(upload_cert=file)
                        upload_f.save()
                        update_candidate.upload_cert.add(upload_f)
                if upload_resume:
                    for file in upload_resume:
                        upload_f = models.AMCandidateUploadResumeModel(upload_resume=file)
                        upload_f.save()
                        update_candidate.upload_resume.add(upload_f)
                if upload_work_video:
                    for file in upload_work_video:
                        upload_f = models.AMCandidateUploadWorkVideoModel(upload_work_video=file)
                        upload_f.save()
                        update_candidate.upload_work_video.add(upload_f)
                if upload_interview_audio:
                    for file in upload_interview_audio:
                        upload_f = models.AMCandidateUploadInterviewAudioModel(upload_interview_audio=file)
                        upload_f.save()
                        update_candidate.upload_interview_audio.add(upload_f)
                update_candidate.save()

                try:
                    return_url = url_encode_func(return_url, encode=False)
                    msg, status = 'Done', 'success'
                    messages.success(request, f'Candidate: {candidate_name} Updated..')
                except Exception as e:
                    msg, status = str(e), 'error'
                    messages.error(request, f'Error: {e}')
                    return_url='/agent-candidate/agent-management-candidate-list'
                response_datas = {'status': status, 'msg': msg, 'return_url': str(return_url)}
            except Exception as e:
                response_datas = {'status': 'error', 'msg': str(e)}
            return JsonResponse(response_datas)
        else:
            try:
                agent = models.AgentManagementNewAgentModel.objects.get(id=agent_name)
                func_candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=agent)
                code_number = get_agent_code_number(func_candidates)
                try:
                    candidate_dob = datetime.strptime(candidate_dob, '%d/%m/%Y')
                except:
                    candidate_dob = None
                chk_dup = request.POST.get('duplicate')
                cand_chk = models.AgentManagementCandidataFormModel.objects.filter(candidate_name=candidate_name,
                                                                candidate_dob=candidate_dob)
                if cand_chk and chk_dup is None:
                    msg = f'{candidate_name} / {candidate_dob} Already Exist!'
                    messages.error(request, msg)
                    response_datas = {'status': 'error', 'msg': msg}
                    return JsonResponse(response_datas)
                any_physical_challenge = True if any_physical_challenge == 'y' else False
                any_relatives = True if any_relatives == 'y' else False
                # sat_salary = sat_salary if sat_salary else None
                new_candidate = models.AgentManagementCandidataFormModel(
                    agent=agent, candidate_dob=candidate_dob, candidate_high_edu=candidate_high_edu,
                    abroad_exp=abroad_exp, sg_pass_detail=sg_pass_detail, applied_pass=applied_pass,
                    specify_note=specify_note, selection_command=selection_command, alternative_position=alternative_position,
                    candidate_name=candidate_name, kyc=kyc, current_location=current_location, local_exp=local_exp,
                    applied_position=applied_position, spouse_dob=spouse_dob, any_physical_challenge=any_physical_challenge,
                    specify_physical_challenge=specify_physical_challenge, any_relatives=any_relatives,
                    specify_any_relatives=specify_any_relatives, code_number=code_number, passport_no=passport_no,
                )
                new_candidate.save()
                for file in upload_passport:
                    upload_f = models.AMCandidateUploadPassportModel(upload_passport=file)
                    upload_f.save()
                    new_candidate.upload_passport.add(upload_f)
                for file in upload_video:
                    upload_f = models.AMCandidateUploadVideoModel(upload_video=file)
                    upload_f.save()
                    new_candidate.upload_video.add(upload_f)
                for file in upload_cert:
                    upload_f = models.AMCandidateUploadCertModel(upload_cert=file)
                    upload_f.save()
                    new_candidate.upload_cert.add(upload_f)
                for file in upload_resume:
                    upload_f = models.AMCandidateUploadResumeModel(upload_resume=file)
                    upload_f.save()
                    new_candidate.upload_resume.add(upload_f)
                for file in upload_work_video:
                    upload_f = models.AMCandidateUploadWorkVideoModel(upload_work_video=file)
                    upload_f.save()
                    new_candidate.upload_work_video.add(upload_f)
                for file in upload_interview_audio:
                    upload_f = models.AMCandidateUploadInterviewAudioModel(upload_interview_audio=file)
                    upload_f.save()
                    new_candidate.upload_interview_audio.add(upload_f)
                messages.success(request, f'New Candidate: {candidate_name} Added.')
                response_datas = {'status': 'success', 'msg': 'Done..'}
            except Exception as e:
                messages.error(request, f'Error: {e}')
                response_datas = {'status': 'error', 'msg': str(e)}
            return JsonResponse(response_datas)
    response_datas = {'status': 'error', 'msg': f'{request.method}'}
    messages.error(request, f'Error: {request.method}')
    return JsonResponse(response_datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementDeleteFileView(View):
    def get(self, request, candidate_id, id, return_url, colname):
        try:
            if 'upload_passport' in colname:
                candidate = models.AMCandidateUploadPassportModel.objects.get(id=id)
                filename = candidate.upload_passport
                os.remove(filename.path)
                candidate.delete()
            elif 'upload_video' in colname:
                candidate = models.AMCandidateUploadVideoModel.objects.get(id=id)
                filename = candidate.upload_video
                os.remove(filename.path)
                candidate.delete()
            elif 'upload_cert' in colname:
                candidate = models.AMCandidateUploadCertModel.objects.get(id=id)
                filename = candidate.upload_cert
                os.remove(filename.path)
                candidate.delete()
            elif 'upload_resume' in colname:
                candidate = models.AMCandidateUploadResumeModel.objects.get(id=id)
                filename = candidate.upload_resume
                os.remove(filename.path)
                candidate.delete()
            elif 'upload_work_video' in colname:
                candidate = models.AMCandidateUploadWorkVideoModel.objects.get(id=id)
                filename = candidate.upload_work_video
                os.remove(filename.path)
                candidate.delete()
            elif 'upload_interview_audio' in colname:
                candidate = models.AMCandidateUploadInterviewAudioModel.objects.get(id=id)
                filename = candidate.upload_interview_audio
                os.remove(filename.path)
                candidate.delete()
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect(f'/agent-candidate/agent-management-candidate-form/{candidate_id}/{return_url}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementCandidateFormView(View):
    template_name = 'agent-management-candidate-form.html'
    def get(self, request, id=None, return_url=None):
        agents = models.AgentManagementNewAgentModel.objects.all()
        datas = {
            'agents': agents
        }
        if id:
            try:
                candidate=models.AgentManagementCandidataFormModel.objects.get(id=id)
                datas['candidate']=candidate
                datas['return_url']=return_url
                try:
                    datas['candidate_dob']=candidate.candidate_dob.strftime('%d/%m/%Y')
                except: pass
            except: pass
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Cadidate Form Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementCandidateListView(View):
    template_name = 'agent-management-candidate-list.html'
    def get(self, request, status=None):
        keyword = request.GET.get('keyword')
        agent_search = request.GET.get('agent-name')
        search_position = request.GET.get('search-position')
        get_url = request.get_full_path()
        if '?keyword' in get_url or '&keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        agents = models.AgentManagementNewAgentModel.objects.all()
        positions = models.AgentManagementCandidataFormModel.objects.values('applied_position').annotate(
                count=Count('applied_position'))
        if status == 'applied':
            title = 'Applied'
            if agent_search or search_position:
                if keyword and agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status='applied').filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword))
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
                elif agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status='applied')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
                elif agent_search:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, status='applied')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
                elif search_position:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(applied_position__icontains=search_position, status='applied')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
                elif keyword:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword)).filter(status='applied')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')

            else:
                try:
                    if keyword:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword)).filter(status='applied')
                    else:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
                except:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(status='applied')
        elif status == 'withdraw':
            title = 'Withdraw'
            if agent_search or search_position:
                if keyword and agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status='withdraw').filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword))
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
                elif agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status='withdraw')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
                elif agent_search:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, status='withdraw')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
                elif search_position:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(applied_position__icontains=search_position, status='withdraw')
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
                elif keyword:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw').filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword))
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
            else:
                if keyword:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(Q(agent__name__icontains=keyword)|
                        Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                        Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                        Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                        Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                        Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                        Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword)).filter(status='withdraw')
                else:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(status='withdraw')
        else:
            title = 'Overall'
            if agent_search or search_position:
                if keyword and agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status__isnull=True).filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword))
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
                elif agent_search and search_position:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, applied_position__icontains=search_position, status__isnull=True)
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
                elif agent_search:
                    try:
                        ag = agents.get(id=agent_search)
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(agent=ag, status__isnull=True)
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
                elif search_position:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(applied_position__icontains=search_position, status__isnull=True)
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
                elif keyword:
                    try:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True).filter(Q(agent__name__icontains=keyword)|
                            Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                            Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                            Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                            Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                            Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                            Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword))
                    except:
                        candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
            else:
                if keyword:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(Q(agent__name__icontains=keyword)|
                        Q(candidate_dob__icontains=keyword)|Q(candidate_high_edu__icontains=keyword)|Q(abroad_exp__icontains=keyword)|
                        Q(sg_pass_detail__icontains=keyword)|Q(applied_pass__icontains=keyword)|Q(specify_note__icontains=keyword)|
                        Q(sat_salary__icontains=keyword)|Q(selection_command__icontains=keyword)|Q(candidate_name__icontains=keyword)|
                        Q(kyc__icontains=keyword)|Q(current_location__icontains=keyword)|Q(local_exp__icontains=keyword)|
                        Q(applied_position__icontains=keyword)|Q(spouse_dob__icontains=keyword)|Q(specify_physical_challenge__icontains=keyword)|
                        Q(specify_any_relatives__icontains=keyword)|Q(passport_no__icontains=keyword)).filter(status__isnull=True)
                else:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(status__isnull=True)
        candidates_page = Paginator(candidates, 25)
        page_number = request.GET.get('page')
        companies = AddCompanyModel.objects.all()
        try:
            candidates_page = candidates_page.get_page(page_number)
        except PageNotAnInteger:
            candidates_page = candidates_page.page(1)
        except EmptyPage:
            candidates_page = candidates_page.page(candidates_page.num_pages)
        datas = {
            'candidates': candidates_page,
            'agents': agents,
            'current_url': current_url,
            'keyword': keyword,
            'agent_search': agent_search,
            'positions': positions,
            'search_positions': search_position,
            'title': title,
            'companies': companies,
            'result_cnt': candidates.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Cadidate List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class UpdateCandidateStatusView(View):
    def get(self, request, id, status, is_remove):
        try:
            candidate = models.AgentManagementCandidataFormModel.objects.get(id=id)
            if is_remove == 0:
                if status == 'applied':
                    candidate.status = status
                    candidate.save()
                    messages.success(request, f'{candidate.candidate_name} Moved to Applied')
                elif status == 'withdraw':
                    candidate.status = status
                    candidate.save()
                    messages.success(request, f'{candidate.candidate_name} Moved to Withdraw')
            elif is_remove == 1:
                if status == 'applied':
                    candidate.status = None
                    candidate.save()
                    messages.success(request, f'{candidate.candidate_name} Moved to Overall')
                    return redirect('/agent-candidate/agent-management-candidate-list/applied')
                elif status == 'withdraw':
                    candidate.status = None
                    candidate.save()
                    messages.success(request, f'{candidate.candidate_name} Moved to Overall')
                    return redirect('/agent-candidate/agent-management-candidate-list/withdraw')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/agent-candidate/agent-management-candidate-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentManagementCandidateDeleteView(View):
    def get(self, request, id):
        try:
            candidate = models.AgentManagementCandidataFormModel.objects.get(id=id)
            candidate_name = candidate.candidate_name
            candidate.delete()
            db_logger.info(f'<b style="color:red">{request.user}</b>: Delete {candidate_name} Candidate')
            messages.success(request, f'{candidate_name} Deleted..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/agent-candidate/agent-management-candidate-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CanadidateCodeNumberUpdateAPI(View):
    def get(self, request, id, code_value):
        try:
            candidate = models.AgentManagementCandidataFormModel.objects.get(id=id)
            candidate.code_number = code_value
            candidate.save()
            response_status = {'status': 'success', 'value': str(candidate.code_number)}
        except Exception as e:
            response_status = {'status': 'error'}
        return JsonResponse(response_status)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CandidateSearchView(View):
    template_name = 'agent-candidate-search.html'
    def get(self, request):
        candidate_name = request.GET.get('candidate-name')
        dob = request.GET.get('dob')
        get_url = request.get_full_path()
        if '?' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        datas = {}
        if candidate_name or dob:
            try:
                dob = datetime.strptime(dob, '%d/%m/%Y').date()
            except: pass
            if candidate_name and dob:
                candidates = models.AgentManagementCandidataFormModel.objects.filter(
                    candidate_name__icontains=candidate_name, candidate_dob__icontains=dob)
            else:
                if candidate_name:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(
                                    candidate_name__icontains=candidate_name)
                elif dob:
                    candidates = models.AgentManagementCandidataFormModel.objects.filter(
                                    candidate_dob__icontains=dob)
            candidates_page = Paginator(candidates, 25)
            page_number = request.GET.get('page')
            try:
                candidates_page = candidates_page.get_page(page_number)
            except PageNotAnInteger:
                candidates_page = candidates_page.page(1)
            except EmptyPage:
                candidates_page = candidates_page.page(candidates_page.num_pages)
            datas['candidates'] = candidates_page
            datas['current_url'] = current_url
            datas['candidate_name'] = candidate_name
            datas['candidate_dob'] = dob
            datas['result_cnt'] = candidates.count()
            datas['return_url'] = url_encode_func(request.get_full_path())
        return render(request, self.template_name, context=datas)

class AssignCandidateToCompanyView(View):
    def get(self, request, candid):
        candidate = models.AgentManagementCandidataFormModel.objects.get(id=candid)
        response_data = {'candidate': candidate.candidate_name}
        return JsonResponse(response_data)
    def post(self, request, candid):
        comp = request.POST.get('company')
        try:
            from uuid import uuid4
            candidate = models.AgentManagementCandidataFormModel.objects.get(id=candid)
            comp = AddCompanyModel.objects.get(id=comp)
            chk_comp = models.CandidateAssignCompanyModel.objects.filter(company=comp)
            if chk_comp:
                assign_cand = chk_comp.first()
                cand = assign_cand.candidates.filter(id=candidate.id)
                if cand:
                    messages.error(request, f'{candidate.candidate_name} Already Exists')
                    response_data = {'status': 'error', 'msg': f'{candidate.candidate_name} Already Exists'}
                    return JsonResponse(response_data)
                else:
                    assign_cand.candidates.add(candidate)
            else:
                unique_id = uuid4()
                assign_cand = models.CandidateAssignCompanyModel(company=comp, unique_id=unique_id)
                assign_cand.save()
                assign_cand.candidates.add(candidate)
            messages.success(request, f'{candidate.candidate_name} Assigned - {comp.company_name}')
            response_data = {'status': 'success', 'msg': 'Done'}
        except Exception as e:
            messages.error(request, f'Error: {e}')
            response_data = {'status': 'error', 'msg': f'Error: {e}'}
        return JsonResponse(response_data)

class AssignedCandidateListView(View):
    template_name = 'assigned-candidate-list.html'
    def get(self, request):
        assigned_candidates = models.CandidateAssignCompanyModel.objects.all()
        datas = {'companies': assigned_candidates}
        return render(request, self.template_name, context=datas)

class AssignedCandidatePageView(View):
    template_name = 'assigned-candidates-view-page.html'
    def get(self, request, id):
        try:
            assigned_candidates = models.CandidateAssignCompanyModel.objects.get(id=id)
            comp = assigned_candidates.company
            datas = {'candidates': assigned_candidates.candidates.all(),
                     'comp': comp,
                     'assigned_id': assigned_candidates,
                     'unique_id': assigned_candidates.unique_id,
                     }
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/agent-candidate/assigned-candidate-lists')
        return render(request, self.template_name, context=datas)

class ReadOnlyCandidateView(View):
    template_name = 'read-only-candidate-view.html'
    def get(self, request, id, unique_id):
        try:
            assigned_candidates = models.CandidateAssignCompanyModel.objects.get(id=id, unique_id=unique_id)
            comp = assigned_candidates.company
            datas = {'candidates': assigned_candidates.candidates.all(),
                     'comp': comp,
                     'unique_id': assigned_candidates.unique_id,
                     }
        except Exception as e:
            datas = {}
        return render(request, self.template_name, context=datas)
