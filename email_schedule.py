import os, django, io
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mio.settings')
from mio import settings
django.setup()

from mom_application import models
from mom_application.views import extract_insert_email
from imap_tools import MailBox, AND
from datetime import datetime

all_emails = models.EmailCredentialModel.objects.all()
for indx, ec in enumerate(all_emails, 1):
    try:
        with MailBox('imap.gmail.com').login(str(ec.gmail_id).strip(), str(ec.gmail_app_password).strip()) as mailbox:
            unread_emails = mailbox.fetch(AND(seen=False), reverse=True)
            read_emails = mailbox.fetch(AND(seen=True), reverse=True)
            try:
                # unread emails
                extract_insert_email(unread_emails, ec, False)
            except Exception as e:
                print('Unread :', e)
            try:
                # read emails
                extract_insert_email(read_emails, ec, True)
            except Exception as e:
                print('Read :', e)
            print(f'{datetime.today()} - {ec.gmail_id} :', ec.gmail_id)
            try:
                ec.gmail_working_status = True
                ec.save()
            except: pass
    except Exception as e:
        try:
            ec.gmail_working_status = False
            ec.save()
        except:
            pass
        print(f'{datetime.today()} - {ec.gmail_id} (Error) :', e)

def get_server_info():
    from job_advertisement.models import ServerStorageInfoModel
    size_cmd = 'df -h'
    size_info = os.popen(size_cmd).read()
    data = size_info.splitlines()
    used_storage = total_storage = percent_used = ''
    try:
        for d in data:
            f = d.split()
            if f:
                if f[0] == '/dev/sda1':
                    x = d.split()
                    used_storage = x[2]
                    total_storage = x[1]
                    percent_used = x[4]
    except: pass

    if ServerStorageInfoModel.objects.count() == 0:
        create_info = ServerStorageInfoModel(total_storage=total_storage,
            user_storage=used_storage, total_percent_used=percent_used)
        create_info.save()
    else:
        update_info = ServerStorageInfoModel.objects.first()
        update_info.total_storage = total_storage
        update_info.user_storage = used_storage
        update_info.total_percent_used = percent_used
        update_info.save()

get_server_info()

def update_dashboard():
    from django.db.models import Q, Sum
    from client_management.models import NewClientModel, AddCompanyModel, BuyingSellingModel
    from job_advertisement.models import JobAdvertisementModel, ServerStorageInfoModel
    from mom_application.models import (EmailTrackerModel, EmailCredentialModel,
                                        WorkPassModel, CreateApplicationQueueModel)
    from agent_candidate import models

    clients = NewClientModel.objects.count()
    companies = AddCompanyModel.objects.count()
    buy_sell = BuyingSellingModel.objects.count()
    today = datetime.today().date()
    jobs = JobAdvertisementModel.objects.count()
    matured_jobs = JobAdvertisementModel.objects.filter(maturity_date__lte=today, expiry_date__gte=today,
                                                            date_of_review__isnull=True)
    staff_needed = BuyingSellingModel.objects.aggregate(Sum('staff_needed'))['staff_needed__sum']

    agent_cnt = models.AgentManagementNewAgentModel.objects.count()
    candidates = models.AgentManagementCandidataFormModel.objects.count()

    email_tracker = EmailTrackerModel.objects.count()
    email_users = EmailCredentialModel.objects.count()
    read_mails = EmailTrackerModel.objects.filter(read_status=True).count()
    unread_mails = EmailTrackerModel.objects.filter(read_status=False).count()

    app_queue_cnt = CreateApplicationQueueModel.objects.count()

    overall_workpass = WorkPassModel.objects.count()
    pending_workpass = WorkPassModel.objects.filter(status__icontains='pending').exclude(status__icontains='doc').count()
    pending_doc_workpass = WorkPassModel.objects.filter(status__icontains='pending').filter(status__icontains='doc').count()
    approve_workpass = WorkPassModel.objects.filter(Q(status__icontains='approved')|Q(status__iexact='valid')).count()
    invalid_workpass = WorkPassModel.objects.filter(Q(status__icontains='reject')|Q(status__icontains='invalid')).count()
    workpass_counts = [overall_workpass, [pending_workpass, round((pending_workpass/overall_workpass)*100)],
                        [pending_doc_workpass, round((pending_doc_workpass/overall_workpass)*100)],
                        [approve_workpass, round((approve_workpass/overall_workpass)*100)],
                        [invalid_workpass, round((invalid_workpass/overall_workpass)*100)]]

    email_not_works = EmailCredentialModel.objects.filter(gmail_working_status=False)
    email_not_works_list = '<br>'.join([f"{i}. {e.gmail_id}" for i, e in enumerate(email_not_works, 1)])
    email_not_works_cnt = email_not_works.count()

    datas = {'clients': clients, 'companies': companies, 'workpass_counts': workpass_counts,
            'staff_needed': staff_needed, 'buy_sell_cnt': buy_sell, 'email_users': email_users,
            'jobs_cnt': jobs, 'matured_jobs': matured_jobs.count(), 'app_queue_cnt': app_queue_cnt,
            'agent_cnt': agent_cnt, 'candidate_cnt': candidates,'total_email': email_tracker,
            'read_mails': read_mails, 'unread_mails': unread_mails, 'email_not_works_list': email_not_works_list, 'email_not_works_cnt': email_not_works_cnt}
    d = models.DashboardModel(datas=datas)
    d.save()
    print(datas)

update_dashboard()
