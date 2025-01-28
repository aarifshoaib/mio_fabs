from django.shortcuts import render, redirect
from django.views import View
from mom_application import models
from client_management.models import AddCompanyModel, NewClientModel
from datetime import datetime, timedelta
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from job_advertisement.models import JobAdvertisementModel
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pdfplumber, re, base64, pytz, csv
from django.http import JsonResponse
from twocaptcha import TwoCaptcha
import requests, os, imaplib, email, email.header
from agent_candidate.models import AgentManagementCandidataFormModel
from bs4 import BeautifulSoup

def url_encode_func(url, encode=True):
    if encode:
        return base64.urlsafe_b64encode(url.encode()).decode()
    return base64.urlsafe_b64decode(url.encode()).decode()

@method_decorator(login_required(login_url="/"), name='dispatch')
class WorkPassStatusView(View):
    template_name = "work-pass-status.html"
    def get(self, request, page_status=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()
        title, clear_filter_url = 'EPOL List', '/mom-application/work-pass-status'
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        if keyword:
            if page_status == 'approved':
                title = 'EPOL List (Approved)'
                clear_filter_url = '/mom-application/work-pass-status/approved'
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword)).filter(Q(status__icontains='approved')|Q(status__iexact='valid'))
            elif page_status == 'pending-doc':
                title = 'EPOL List (Pending Doc)'
                clear_filter_url = '/mom-application/work-pass-status/pending-doc'
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword)).filter(status__icontains='pending').filter(status__icontains='doc')
            elif page_status == 'pending':
                title = 'EPOL List (Pending)'
                clear_filter_url = '/mom-application/work-pass-status/pending'
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword)).filter(status__icontains='pending')
            elif page_status == 'rejected':
                title = 'EPOL List (Rejected)'
                clear_filter_url = '/mom-application/work-pass-status/rejected'
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword)).filter(Q(status__icontains='reject')|Q(status__icontains='invalid'))
            elif page_status == 'daily_status':
                title = 'EPOL List (Daily Status)'
                clear_filter_url = '/mom-application/work-pass-status/daily_status'
                today = datetime.today()
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword)).filter(last_update__year=today.year,
                                                last_update__month=today.month, last_update__day=today.day)
            else:
                title = 'EPOL List (Overall Status)'
                workpass = models.WorkPassModel.objects.filter(Q(application_no__icontains=keyword) |
                            Q(name__icontains=keyword) | Q(company_name__company_name__icontains=keyword) |
                            Q(passport_no__icontains=keyword) | Q(fin_number__icontains=keyword) | Q(epass_type__icontains=keyword) |
                            Q(status__icontains=keyword))
        else:
            if page_status == 'approved':
                title = 'EPOL List (Approved)'
                clear_filter_url = '/mom-application/work-pass-status/approved'
                workpass = models.WorkPassModel.objects.filter(Q(status__icontains='approved')|Q(status__iexact='valid'))
            elif page_status == 'pending-doc':
                title = 'EPOL List (Pending Doc)'
                clear_filter_url = '/mom-application/work-pass-status/pending-doc'
                workpass = models.WorkPassModel.objects.filter(status__icontains='pending').filter(status__icontains='doc')
            elif page_status == 'pending':
                title = 'EPOL List (Pending)'
                clear_filter_url = '/mom-application/work-pass-status/pending'
                workpass = models.WorkPassModel.objects.filter(status__icontains='pending')
            elif page_status == 'rejected':
                title = 'EPOL List (Rejected)'
                clear_filter_url = '/mom-application/work-pass-status/rejected'
                workpass = models.WorkPassModel.objects.filter(Q(status__icontains='reject')|Q(status__icontains='invalid'))
            elif page_status == 'daily_status':
                title = 'EPOL List (Daily Status)'
                clear_filter_url = '/mom-application/work-pass-status/daily_status'
                today = datetime.today()
                workpass = models.WorkPassModel.objects.filter(last_update__year=today.year,
                                                last_update__month=today.month, last_update__day=today.day)
            else:
                title = 'EPOL List (Overall Status)'
                workpass = models.WorkPassModel.objects.all()
        workpass = workpass.order_by('-doa')
        captcha = models.CaptchaIssueModel.objects.count()
        workpass_page = Paginator(workpass, 25)
        page_number = request.GET.get('page')

        try:
            workpass_page = workpass_page.get_page(page_number)
        except PageNotAnInteger:
            workpass_page = workpass_page.page(1)
        except EmptyPage:
            workpass_page = workpass_page.page(workpass_page.num_pages)
        if captcha != 0:
            try:
                l = models.CaptchaIssueModel.objects.first()
                error = l.error
                captcha_cnt = l.balance
                last_update = l.last_update.strftime('%d-%m-%Y %H:%M:%S')
            except Exception:
                error, captcha_cnt, last_update = False, None, None
        else:
            error, captcha_cnt, last_update = False, None, None

        datas = {
            'workpass_page': workpass_page,
            'current_url': current_url,
            'error': error,
            'last_update': last_update,
            'captcha_cnt': captcha_cnt,
            'keyword': keyword,
            'result_cnt': workpass.count(),
            'pending_cnt': models.WorkPassModel.objects.filter(status='PENDING').count(),
            'approved_cnt': models.WorkPassModel.objects.filter(Q(status__icontains='approved')|Q(status__iexact='valid')).count(),
            'rejected_cnt': models.WorkPassModel.objects.filter(Q(status__icontains='reject')|Q(status__icontains='invalid')).count(),
            'return_url': url_encode_func(request.get_full_path()),
            'title': title,
            'clear_filter_url': clear_filter_url,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateWorkPassView(View):
    template_name = "create-workpass.html"
    def get(self, request, id=None, return_url=None):
        companies = AddCompanyModel.objects.all()
        datas = {
            'companies': companies,
            'jobs': JobAdvertisementModel.objects.all(),
        }
        if id:
            workpass = models.WorkPassModel.objects.get(id=id)
            datas['edit_workpass'] = workpass
            try:
                datas['edit_wp_dob'] = workpass.dob.strftime('%d-%m-%Y')
                datas['edit_wp_doa'] = workpass.doa.strftime('%d-%m-%Y')
            except: pass
        return render(request, self.template_name, context=datas)

    def post(self, request, id=None, return_url=None):
        doa = request.POST.get('doa')
        application_no = request.POST.get('app-no')
        company = request.POST.get('company')
        passport_no = request.POST.get('passport-no')
        status = request.POST.get('status') if request.POST.get('status') else 'PENDING'
        person_name = request.POST.get('name')
        fin_number = request.POST.get('fin')
        dob = request.POST.get('dob')
        epass_type = request.POST.get('epass_type')
        job_code = request.POST.get('job-code')
        source = request.POST.get('source')
        apply_copy = request.FILES.get('apply-copy')
        try:
            dob = datetime.strptime(dob, '%d/%m/%Y')
            doa = datetime.strptime(doa, '%d/%m/%Y')
        except Exception:
            messages.error(request, "Error : DOA & DOB DateFormat Should be dd/mm/yyyy")
            return redirect('/mom-application/create-workpass')

        try:
            company = AddCompanyModel.objects.get(id=company)
        except Exception:
            company = None

        try:
            if job_code == 'Not Available':
                job_code = None
                not_available = True
            else:
                job_code = JobAdvertisementModel.objects.get(id=job_code)
                not_available = False
        except Exception:
            job_code = None
            not_available = False

        if models.WorkPassModel.objects.filter(application_no=application_no) and id is None:
            messages.error(request, f"{application_no} Already Exists!!!")
            return redirect('/mom-application/create-workpass')

        if id is None:
            try:
                workpass = models.WorkPassModel(application_no=application_no, name=person_name, company_name=company,
                                                passport_no=passport_no, fin_number=fin_number, dob=dob, status=status,
                                                epass_type=epass_type, doa=doa, job=job_code, not_available=not_available,
                                                source=source, apply_copy=apply_copy)
                workpass.save()
                messages.success(request, f"New EPOL {passport_no} Created.")
            except Exception as e:
                messages.error(request, f"Error : {e}")
        else:
            try:
                workpass = models.WorkPassModel.objects.get(id=id)
                workpass.application_no = application_no
                workpass.name = person_name
                workpass.company_name = company
                workpass.passport_no = passport_no
                workpass.fin_number = fin_number
                workpass.dob = dob
                workpass.status = status
                workpass.doa = doa
                workpass.epass_type = epass_type
                workpass.job = job_code
                workpass.not_available = not_available
                workpass.source = source
                if apply_copy:
                    workpass.apply_copy = apply_copy
                workpass.save()
                messages.success(request, f"Passport No. {passport_no} Updated.")
            except Exception as e:
                messages.error(request, f"Error : {e}")
        if return_url:
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                pass
        return redirect('/mom-application/create-workpass')

@method_decorator(login_required(login_url="/"), name='dispatch')
class PendingDocUploadImageView(View):
    def post(self, request, id, page):
        try:
            upload_img = request.FILES.get('upload-image')
            workpass = models.WorkPassModel.objects.get(id=id)
            if request.FILES:
                workpass.pending_doc = upload_img
                workpass.save()
                messages.success(request, f"{upload_img} Uploaded..")
        except Exception as e:
            messages.error(request, f"Error : {e}")
        return redirect(f'/mom-application/work-pass-status/pending-doc?page={page}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class RejectedReasonDocUploadView(View):
    def post(self, request, id, page):
        try:
            reason_doc = request.FILES.get('reason-doc')
            workpass = models.WorkPassModel.objects.get(id=id)
            if request.FILES:
                workpass.rejected_reason = reason_doc
                workpass.save()
                messages.success(request, f"{reason_doc} Uploaded..")
        except Exception as e:
            messages.error(request, f"Error : {e}")
        return redirect(f'/mom-application/work-pass-status/rejected?page={page}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteWorkPassView(View):
    def get(self, request, id):
        try:
            workpass = models.WorkPassModel.objects.get(id=id)
            workpass.delete()
            messages.success(request, f"WorkPass ID {id} Deleted.")
        except Exception as e:
            messages.error(request, f"Error : {e}")
        return redirect('/mom-application/work-pass-status')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AddEmailDetailsView(View):
    template_name = 'add-email-details.html'
    def get(self, request, id=None):
        companies = AddCompanyModel.objects.all()
        datas = {
            'companies': companies,
        }
        if id:
            try:
                edit_email = models.EmailCredentialModel.objects.get(id=id)
                datas['edit_email'] = edit_email
            except Exception as e:
                messages.error(request, f"Error : {e}")
        return render(request, self.template_name, context=datas)

    def post(self, request, id=None):
        comp = request.POST.get('company')
        email_id = request.POST.get('email')
        app_password = request.POST.get('password')

        if id:
            try:
                comp = AddCompanyModel.objects.get(id=comp)
                ec = models.EmailCredentialModel.objects.get(id=id)
                ec.company = comp
                ec.gmail_id = email_id
                ec.gmail_app_password = app_password
                ec.save()
                messages.success(request, f"Email: {email_id} Updated.")
            except Exception as e:
                messages.error(request, f"Error : {e}")
        else:
            try:
                if models.EmailCredentialModel.objects.filter(gmail_id=email_id):
                    messages.error(request, f"{email_id} Already Exists!!")
                    return redirect('/mom-application/add-email-details')
                comp = AddCompanyModel.objects.get(id=comp)
                ec = models.EmailCredentialModel(company=comp, gmail_id=email_id, gmail_app_password=app_password)
                ec.save()
                messages.success(request, f"New Email: {email_id} Added.")
            except Exception as e:
                messages.error(request, f"Error : {e}")
        return redirect('/mom-application/add-email-details')

def text_to_html_convert(text_data):
    html = ''
    try:
        for data in text_data.splitlines():
            if data.strip():
                html = html + "<p>" + data + "</p>\n"
        return html
    except:
        return text_data

def extract_insert_email(email_msg, email_cred, status):
    from django.core.files.base import ContentFile
    for msg in email_msg:
        email_from = msg.from_
        try:
            text, encoding = email.header.decode_header(msg.subject)[0]
            email_subject = text.decode()
        except:
            email_subject = msg.subject

        try:
            utc_time = msg.date
            ist_timezone = pytz.timezone('Asia/Kolkata')
            email_date_time = utc_time.astimezone(ist_timezone)
        except:
            email_date_time = msg.date

        try:
            body = msg.html
            if not body.strip():
                body = text_to_html_convert(msg.text)
        except:
            body = ''

        before5days = (datetime.today().date() + timedelta(hours=5, minutes=30)) - timedelta(days=5)
        if before5days <= email_date_time.date():
            try:
                if models.EmailTrackerModel.objects.filter(email_credential=email_cred, receive_date=email_date_time):
                    continue
                etracker = models.EmailTrackerModel(email_credential=email_cred, from_user=email_from, subject=email_subject,
                                receive_date=email_date_time, body=body, read_status=status)
                etracker.save()
                try:
                    for attach in msg.attachments:
                        add_attach = models.EmailAttachmentsModel()
                        filedata = ContentFile(attach.payload)
                        add_attach.attachments.save(attach.filename, filedata)
                        etracker.attachments.add(add_attach)
                except: pass
            except Exception:
                pass
        else:
            break

def read_email_from_gmail(FROM_EMAIL, FROM_PWD, email_cred):
    from imap_tools import MailBox, AND
    with MailBox('imap.gmail.com').login(FROM_EMAIL, FROM_PWD) as mailbox:
        unread_emails = mailbox.fetch(AND(seen=False), reverse=True)
        read_emails = mailbox.fetch(AND(seen=True), reverse=True)

        try:
            # unread emails
            extract_insert_email(unread_emails, email_cred, False)
        except: pass

        try:
            # read emails
            extract_insert_email(read_emails, email_cred, True)
        except: pass

def send_reply_mail(gmail, passwrd, to_addr, subject, html_text, filenames):
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = gmail
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(html_text, 'html'))

    for file in filenames:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
        msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail, passwrd)
    mailServer.sendmail(gmail, to_addr, msg.as_string())
    mailServer.close()

def fetch_new_email(request, id):
    try:
        ec = models.EmailCredentialModel.objects.get(id=id)
        read_email_from_gmail(str(ec.gmail_id).strip(), str(ec.gmail_app_password).strip(), ec)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': f'error: {e}'})

@method_decorator(login_required(login_url="/"), name='dispatch')
class EmailListView(View):
    template_name = 'email-list.html'
    def get(self, request, id):
        try:
            get_url = request.get_full_path()
            keyword = request.GET.get('keyword')

            if '?keyword' in get_url:
                get_url = get_url.split('&page=')[0]
                current_url = f"{get_url}&"
            else:
                get_url = get_url.split('?')[0]
                current_url = f"{get_url}?"

            ec = models.EmailCredentialModel.objects.get(id=id)
            etracker = models.EmailTrackerModel.objects.filter(email_credential=ec)

            if keyword:
                keyword = keyword.lower()
                etracker_body = [ row.id for row in etracker
                                 if str(BeautifulSoup(row.body, 'lxml').text).lower().find(keyword) > -1
                                    or (row.receive_date + timedelta(hours=5, minutes=30)
                                        ).strftime('%B %d, %Y, %I:%M %p').lower().find(keyword) > -1]
                etracker = etracker.filter(
                        Q(from_user__icontains=keyword)|Q(subject__icontains=keyword)|Q(receive_date__icontains=keyword)
                        ).union(etracker.filter(id__in=etracker_body))

            etracker_page = Paginator(etracker.order_by('-receive_date'), 25)
            page_number = request.GET.get('page')

            try:
                etracker_page = etracker_page.get_page(page_number)
            except PageNotAnInteger:
                etracker_page = etracker_page.page(1)
            except EmptyPage:
                etracker_page = etracker_page.page(etracker_page.num_pages)
            datas = {'email_datas': etracker_page, 'ec': ec, 'current_url': current_url, 'keyword': keyword}
            return render(request, self.template_name, context=datas)
        except:
            return redirect('/mom-application/email-credentials')

def search_email_autocomplete(request, to_mail, value):

    try:
        to_email = models.EmailCredentialModel.objects.get(id=to_mail)
        filtered_datas = models.EmailTrackerModel.objects.filter(email_credential=to_email).filter(
                Q(from_user__icontains=value)|Q(subject__icontains=value)|Q(receive_date__icontains=value)|
                Q(body__icontains=value))
        values = set()
        for data in filtered_datas:
            value = value.lower()
            if data.from_user.lower().find(value) > -1:
                values.add(data.from_user)
            if data.subject.lower().find(value) > -1:
                values.add(data.subject)
            receive_date = (data.receive_date + timedelta(hours=5, minutes=30)).strftime('%B %d, %Y, %I:%M %p')
            if receive_date.lower().find(value) > -1:
                values.add(receive_date)
            soup_text = BeautifulSoup(str(data.body), 'lxml').text.lower()
            body_indx = soup_text.find(value)
            body = f'{soup_text[body_indx:body_indx+10]}'
            if body_indx > -1:
                values.add(body)
        response_datas = {'status': 'success', 'values': list(values)}
    except Exception as e:
        response_datas = {'status': 'error', 'msg': f'{e}'}
    return JsonResponse(response_datas)

def old_read_email_from_gmail(FROM_EMAIL, FROM_PWD, email_cred):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(FROM_EMAIL,FROM_PWD)
    mail.select('inbox')

    data = mail.search(None, 'ALL')
    mail_ids = data[1]
    id_list = mail_ids[0].split()
    first_email_id = int(id_list[0])
    latest_email_id = int(id_list[-1])

    for i in range(latest_email_id,first_email_id, -1):
        data, break_point = mail.fetch(str(i), '(RFC822)' ), False
        for response_part in data:
            arr = response_part[0]
            if isinstance(arr, tuple):
                msg = email.message_from_string(str(arr[1],'utf-8'))
                try:
                    text, encoding = email.header.decode_header(msg['subject'])[0]
                    email_subject = text.decode()
                except:
                    email_subject = msg['subject']
                email_from = msg['from']
                email_date_time = msg['Date']
                try:
                    timeee = email_date_time.replace('GMT', '+0530').split(" ")
                    dd, tzz = -1, -1
                    for i in timeee:
                        if i.isdigit():
                            if len(i) == 1 or len(i) == 2:
                                dd = timeee.index(i)
                        if ':' in i:
                            tzz = timeee.index(i) + 2

                    utc = datetime.strptime(' '.join(timeee[dd:tzz][:-1]), '%d %b %Y %H:%M:%S')
                    get_tzz = timeee[dd:tzz][1:][-1][1:]

                    if 'GMT' in email_date_time:
                        tz_hour = int(str(get_tzz[:2]))
                        tz_minute = int(str(get_tzz[2:]))
                        tzone = timedelta(hours=tz_hour, minutes=tz_minute)
                        ist = timedelta(hours=5, minutes=30)
                        ist_time = (utc + tzone)
                        ist_time = datetime.strftime(ist_time, "%Y-%m-%d %H:%M:%S")
                        convert_datetime = datetime.strptime(ist_time, "%Y-%m-%d %H:%M:%S")
                    elif '0530' not in get_tzz:
                        tz_hour = int(str(get_tzz[:2]))
                        tz_minute = int(str(get_tzz[2:]))
                        tzone = timedelta(hours=tz_hour, minutes=tz_minute)
                        ist = timedelta(hours=5, minutes=30)
                        ist_time = (utc + tzone) + ist
                        ist_time = datetime.strftime(ist_time, "%Y-%m-%d %H:%M:%S")
                        convert_datetime = datetime.strptime(ist_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        convert_datetime = datetime.strftime(utc, "%Y-%m-%d %H:%M:%S")
                        convert_datetime = datetime.strptime(convert_datetime, "%Y-%m-%d %H:%M:%S")
                    email_date_time = convert_datetime
                except Exception:
                    pass

                body = ''
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True)
                try:
                    body = body.decode()
                except: pass

                if 'datetime' in str(type(email_date_time)):
                    before5days = datetime.today().date() - timedelta(days=5)
                    if before5days <= email_date_time.date():
                        try:
                            if models.EmailTrackerModel.objects.filter(receive_date=email_date_time):
                                continue
                            etracker = models.EmailTrackerModel(email_credential=email_cred, from_user=email_from, subject=email_subject,
                                            receive_date=email_date_time, body=body)
                            etracker.save()
                        except Exception:
                            pass
                    else:
                        break_point = True
                        break
                else:
                    try:
                        if models.EmailTrackerModel.objects.filter(receive_date=email_date_time):
                            continue
                        etracker = models.EmailTrackerModel(email_credential=email_cred, from_user=email_from, subject=email_subject,
                                        receive_date=email_date_time, body=body)
                        etracker.save()
                    except Exception:
                        pass

        if break_point:
            break

@method_decorator(login_required(login_url="/"), name='dispatch')
class ReplyMailAPI(View):
    def post(self, request, emailtracker_id):
        subject = request.POST.get('subject')
        message_html = request.POST.get('message')
        attachments = request.FILES.getlist('attachments')
        try:
            emailtracker = models.EmailTrackerModel.objects.get(id=emailtracker_id)
            to_addr = emailtracker.from_user
            from_addr = emailtracker.email_credential.gmail_id
            passwrd = emailtracker.email_credential.gmail_app_password
            send_reply_mail(from_addr, passwrd, to_addr, subject, message_html, attachments)
            messages.success(request, 'Mail Sent..')
            response_data = {
                'status': 'success', 'msg': 'Mail Sent',
            }
        except Exception as e:
            response_data = {
                'status': 'error', 'msg': str(e),
            }
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class UnreadMailView(View):
    template_name='unread-mail.html'
    def get(self, request):
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        all_mails = models.EmailTrackerModel.objects.filter(read_status=False).order_by('-receive_date')

        all_mails_page = Paginator(all_mails, 25)
        page_number = request.GET.get('page')
        try:
            all_mails_page = all_mails_page.get_page(page_number)
        except PageNotAnInteger:
            all_mails_page = all_mails_page.page(1)
        except EmptyPage:
            all_mails_page = all_mails_page.page(all_mails_page.num_pages)
        datas = {'all_mails': all_mails_page, 'total_emails': all_mails.count(), 'current_url': current_url}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class EmailCredentialView(View):
    template_name = 'email-credentials.html'
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
            gmail_credentials = models.EmailCredentialModel.objects.filter(
                    Q(company__company_id__icontains=keyword)|Q(company__company_name__icontains=keyword)|
                    Q(gmail_id__icontains=keyword)).order_by('company__client__client_id', 'company__company_id')
        else:
            gmail_credentials = models.EmailCredentialModel.objects.all().order_by(
                'company__client__client_id', 'company__company_id')

        gmail_credentials_page = Paginator(gmail_credentials, 25)
        page_number = request.GET.get('page')
        try:
            gmail_credentials_page = gmail_credentials_page.get_page(page_number)
        except PageNotAnInteger:
            gmail_credentials_page = gmail_credentials_page.page(1)
        except EmptyPage:
            gmail_credentials_page = gmail_credentials_page.page(gmail_credentials_page.num_pages)
        datas = {'gmail_credentials': gmail_credentials_page,
                 'current_url': current_url,
                 'keyword': keyword,
                 'result_cnt': gmail_credentials.count(),
            }

        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ReadEmailView(View):
    template_name = 'email-details-view.html'
    def get(self, request, id):
        try:
            read_email = models.EmailTrackerModel.objects.get(id=id)
            try:
                read_email.read_status = True
                read_email.save()
            except: pass
            datas = {
                'read_email': read_email,
            }
            return render(request, self.template_name, context=datas)
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/mom-application/email-credentials')

@method_decorator(login_required(login_url="/"), name='dispatch')
class PrintEmailView(View):
    template_name = 'print-email.html'
    def get(self, request, id):
        read_email = models.EmailTrackerModel.objects.get(id=id)
        datas = {
            'read_email': read_email,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ReadAllUnreadMailsView(View):
    def get(self, request, page=None):
        try:
            if page:
                try:
                    page_number = page
                    all_mails = models.EmailTrackerModel.objects.filter(read_status=False).order_by('-receive_date')
                    all_mails_page = Paginator(all_mails, 25)
                    all_mails_page = all_mails_page.get_page(page_number)

                    curr_page_ids = [i.id for i in all_mails_page]
                    unread_email = all_mails.filter(id__in=curr_page_ids)
                    unread_email.update(read_status=True)
                except:
                    pass
            else:
                unread_email = models.EmailTrackerModel.objects.filter(read_status=False)
                unread_email.update(read_status=True)

            response_data = {'status': 'success'}
        except Exception as e:
            messages.error(request, f'Error: {e}')
            response_data = {'status': 'error'}
        return JsonResponse(response_data)

class CPFExtractor:
    def __init__(self, invoice):
        self.invoice = invoice

    def extract_amount(self, amt):
        try:
            amt = float(re.sub('[^0-9\.]+', '', str(amt)))
        except:
            amt = 0
        return amt

    def parse_table(self):
        lines, start, stop = [], [], []
        for pdf in self.invoice.pages:
            lines.extend(pdf.extract_text().splitlines())
        for indx, line in enumerate(lines):
            if 'S/N CPF' in line:
                start.append(indx)
            if 'Total Amount' in line:
                stop.append(indx)
        if not start or not stop:
            return
        start, stop = min(start), min(stop)
        table = []
        for line in lines[start: stop]:
            if 'Copyright' in line or 'S/N' in line or 'Account' in line or 'No.' in line:
                continue
            table.append(line)
        return self.fix_name(table)

    def fix_name(self, table):
        datas = []
        for line in table:
            data = {
                'SNo': '', 'CPF Account No': '', 'Name of Employee': '', 'CPF To Be Paid': '',
                'SDL To Be Paid': '', 'Employer CPF': '', 'Employee CPF': '', 'Ordinary Wages': '',
                'Additional Wages': '', 'Agency': '', 'Agency Fund': '',
            }
            d = line.split()
            if d[0].replace('.', '').isdigit():
                data['SNo'] = d[0]
                data['CPF Account No'] = d[1]
                data['Name of Employee'] = ' '.join(d[2:-8])
                data['Agency Fund'] = self.extract_amount(d[-1])
                data['Agency'] = self.extract_amount(d[-2])
                data['Additional Wages'] = self.extract_amount(d[-3])
                data['Ordinary Wages'] = self.extract_amount(d[-4])
                data['Employee CPF'] = self.extract_amount(d[-5])
                data['Employer CPF'] = self.extract_amount(d[-6])
                data['SDL To Be Paid'] = self.extract_amount(d[-7])
                data['CPF To Be Paid'] = self.extract_amount(d[-8])
                datas.append(data)
            else:
                datas[-1]['Name of Employee'] = f"{datas[-1]['Name of Employee']} {''.join(d)}"
        return datas

def cpf_csv_Extractor(cpf_csv_file):
    import io
    decoded_file = cpf_csv_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    datas = []
    for line in csv.DictReader(io_string):
        datas.append(line)
    return datas

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFExtractView(View):
    template_name = 'cpf-invoice.html'
    def get(self, request):
        companies = models.AddCompanyModel.objects.all()
        return render(request, self.template_name, context={'companies': companies})

    def post(self, request):
        cpf_pdf = request.FILES.get('cpf-pdf')
        cpf_csv = request.FILES.get('cpf-csv')
        comp = request.POST.get('company')
        contr_date_month = request.POST.get('date-month')
        try:
            cpf_csv_datas = None
            if not cpf_pdf.name.lower().endswith('.pdf'):
                messages.error(request, f'{cpf_pdf.name} not PDF Format..')
                return redirect('/mom-application/cpf-invoice')
            if cpf_csv is not None:
                if not cpf_csv.name.lower().endswith('.csv'):
                    messages.error(request, f'{cpf_csv.name} not CSV Format..')
                    return redirect('/mom-application/cpf-invoice')
                cpf_csv_datas = cpf_csv_Extractor(cpf_csv)
            contr_date_month = datetime.strptime(f'{contr_date_month}-01', '%Y-%m-%d')
            comp = AddCompanyModel.objects.get(id=comp)
            cpf_model = models.CPFInvoiceModel(company=comp, upload_date=datetime.today(),
                            pdf_invoice=cpf_pdf, csv_invoice=cpf_csv, datas=cpf_csv_datas,
                            contribution_date_month=contr_date_month)
            cpf_model.save()
            messages.success(request, 'File Uploaded..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/mom-application/cpf-invoice')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFInvoiceList(View):
    template_name='cpf-list.html'
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
            cpf_data = models.CPFInvoiceModel.objects.filter(Q(company__company_id__icontains=keyword)|
                Q(company__company_name__icontains=keyword)|Q(contribution_date_month__icontains=keyword)
                ).order_by('company__client__client_id', 'company__company_id')
        else:
            cpf_data = models.CPFInvoiceModel.objects.all().order_by('company__client__client_id', 'company__company_id')
        cpf_datas = cpf_data.values('company__id', 'company__company_id', 'company__company_name').annotate(
                count=Count('company__company_name'))
        datas = {
            'cpf_datas': cpf_datas,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': cpf_data.count(),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFFilesList(View):
    template_name='cpf-files-list.html'
    def get(self, request, comp_id):
        try:
            file_details = models.CPFInvoiceModel.objects.filter(company__id=comp_id)
            company = AddCompanyModel.objects.get(id=comp_id)
        except:
            file_details, company = [], ''
        datas = {'file_details': file_details, 'company': company}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteCPFInvoice(View):
    def get(self, request, id):
        try:
            cpf = models.CPFInvoiceModel.objects.get(id=id)
            cpf.delete()
            messages.success(request, f'ID: {id} Deleted..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/mom-application/cpf-list')

def value_search(keyword, data_dict):
    for data in data_dict.values():
        if keyword in data.lower():
            return True
    return False

def search_invoice_json(keyword, datas):
    return filter(lambda data: value_search(keyword, data), datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFInvoiceDetails(View):
    template_name='cpf-invoice-details.html'
    def get(self, request, id):
        keyword = request.GET.get('keyword')
        try:
            cpf_datas = models.CPFInvoiceModel.objects.get(id=id)
            if keyword:
                cpf_datas = list(search_invoice_json(keyword.lower(), cpf_datas.datas))
            else:
                cpf_datas = cpf_datas.datas
            datas = {
                'cpf_datas': cpf_datas,
                'result_cnt': len(cpf_datas),
                'keyword': keyword,
                'clear_filter': f'/mom-application/cpf-invoice-details/{id}'
            }
        except:
            datas = {'clear_filter': f'/mom-application/cpf-invoice-details/{id}'}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AfterApprovalTEPView(View):
    template_name='after-approval-tep.html'
    def get(self, request, id, return_url=None):
        wp = models.WorkPassModel.objects.get(id=id)
        after_approve = models.AfterApprovalTEPModel.objects.filter(workpass=wp)
        datas = {'workpass': wp, 'width': '40%'}
        if after_approve:
            try:
                datas['after_approval'] = after_approve.first()
                after_approve_dict = after_approve.first().__dict__
                datas['valid_field'] = [ i for i in after_approve_dict
                                        if after_approve_dict[i] is not None and after_approve_dict[i] != '']

                if after_approve.first().ipa_expiry_date:
                    try:
                        datas['after_approval_ipa_exp_date'] = after_approve.first().ipa_expiry_date.strftime('%Y-%m-%d')
                    except: pass
                if after_approve.first().arived_traval_date:
                    try:
                        datas['after_approval_arived_traval_date'] = after_approve.first().arived_traval_date.strftime('%Y-%m-%d')
                    except: pass
                if after_approve.first().new_valid:
                    try:
                        datas['after_approval_new_valid'] = after_approve.first().new_valid.strftime('%Y-%m-%d')
                    except: pass
                if after_approve.first().issue:
                    try:
                        datas['after_approval_issue'] = after_approve.first().issue.strftime('%Y-%m-%d')
                    except: pass
                if after_approve.first().card_exp:
                    try:
                        datas['after_approval_card_exp'] = after_approve.first().card_exp.strftime('%Y-%m-%d')
                    except: pass
                if after_approve.first().traval_date:
                    try:
                        datas['after_approval_traval_date'] = after_approve.first().traval_date.strftime('%Y-%m-%d')
                    except: pass
            except: pass
        return render(request, self.template_name, context=datas)

    def post(self, request, id, return_url=None):
        # Stalin Fields
        employee_ind_contact = request.POST.get('emp-ind-contact')
        employee_ind_contact = employee_ind_contact if employee_ind_contact else None
        employee_sg_contact = request.POST.get('emp-sg-contact')
        employee_sg_contact = employee_sg_contact if employee_sg_contact else None
        arived_traval_date = request.POST.get('arived-travel-date')
        try:
            arived_traval_date = datetime.strptime(arived_traval_date, '%Y-%m-%d')
            extension_due_20_days = arived_traval_date + timedelta(days=20)
        except:
            arived_traval_date = None
            extension_due_20_days = None
        new_valid = request.POST.get('new-valid')
        try:
            new_valid = datetime.strptime(new_valid, '%Y-%m-%d')
        except:
            new_valid = None
        traval_date = request.POST.get('travel-date')
        try:
            traval_date = datetime.strptime(traval_date, '%Y-%m-%d')
        except:
            traval_date = None
        issue_docs = request.FILES.get('issue-docs')
        card_status = request.FILES.get('card-status')
        remarks = request.POST.get('remarks')
        upload_ipa = request.FILES.get('upload-ipa')
        ica_upload = request.FILES.get('ica-upload')
        notify_acknowledgement = request.FILES.get('notify-acknowledgement')
        driving = request.POST.get('driving')
        other_assignment = request.POST.get('other-assignment')

        # Ahmed Fields
        ipa_to_agent = request.POST.get('ipa-to-agent')

        # Samiha Fields
        ipa_to_employeer = request.POST.get('ipa-to-employeer')
        ipa_exp_date = request.POST.get('ipa-exp-date')
        try:
            ipa_exp_date = datetime.strptime(ipa_exp_date, '%Y-%m-%d')
        except:
            ipa_exp_date = None
        issue = request.POST.get('issue')
        try:
            issue = datetime.strptime(issue, '%Y-%m-%d')
            thump = issue + timedelta(days=7)
        except:
            issue = None
            thump = None
        card_exp = request.POST.get('card-exp')
        try:
            card_exp = datetime.strptime(card_exp, '%Y-%m-%d')
        except:
            card_exp = None

        # Naseer Fields
        payment = request.POST.get('payment')

        try:
            workpass = models.WorkPassModel.objects.get(id=id)
            if models.AfterApprovalTEPModel.objects.filter(workpass=workpass):
                after_approve = models.AfterApprovalTEPModel.objects.get(workpass=workpass)
                after_approve.arived_traval_date = arived_traval_date
                after_approve.employee_ind_contact=employee_ind_contact
                after_approve.employee_sg_contact=employee_sg_contact
                after_approve.extension_due_20_days = extension_due_20_days
                after_approve.new_valid = new_valid
                after_approve.ipa_to_agent = ipa_to_agent
                if issue_docs:
                    after_approve.issue_docs = issue_docs
                if card_status:
                    after_approve.card_status = card_status
                if upload_ipa:
                    after_approve.upload_ipa = upload_ipa
                if ica_upload:
                    after_approve.ica_upload = ica_upload
                after_approve.remarks = remarks
                after_approve.driving = driving
                after_approve.other_assignment = other_assignment
                after_approve.ipa_to_employer = ipa_to_employeer
                after_approve.ipa_expiry_date = ipa_exp_date
                after_approve.issue = issue
                after_approve.card_exp = card_exp
                after_approve.payment = payment
                after_approve.traval_date = traval_date
                after_approve.thump = thump
                if notify_acknowledgement:
                    after_approve.notify_acknowledgement = notify_acknowledgement
                after_approve.save()
            else:
                after_approve = models.AfterApprovalTEPModel(workpass=workpass, thump=thump, ica_upload=ica_upload,
                    employee_ind_contact=employee_ind_contact, employee_sg_contact=employee_sg_contact, notify_acknowledgement=notify_acknowledgement,
                    arived_traval_date=arived_traval_date, extension_due_20_days=extension_due_20_days, new_valid=new_valid,
                    issue_docs=issue_docs, ipa_to_agent=ipa_to_agent, ipa_to_employer=ipa_to_employeer, traval_date=traval_date,
                    ipa_expiry_date=ipa_exp_date, issue=issue, card_exp=card_exp, payment=payment, upload_ipa=upload_ipa,
                    card_status=card_status, remarks=remarks, driving=driving, other_assignment=other_assignment)
                after_approve.save()
            messages.success(request, f'{workpass.name} Datas Submitted..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        if return_url:
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                pass
        return redirect('/mom-application/work-pass-status/approved')

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteUploadedTEPFileView(View):
    def get(self, request, id, colname):
        try:
            workpass = models.WorkPassModel.objects.get(id=id)
            after_approve = models.AfterApprovalTEPModel.objects.get(workpass=workpass)
            if colname == 'upload_ipa':
                filepath = after_approve.upload_ipa
                os.remove(filepath.path)
                after_approve.upload_ipa = None
                after_approve.save()
            elif colname == 'ica_upload':
                filepath = after_approve.ica_upload
                os.remove(filepath.path)
                after_approve.ica_upload = None
                after_approve.save()
            elif colname == 'issue_docs':
                filepath = after_approve.issue_docs
                os.remove(filepath.path)
                after_approve.issue_docs = None
                after_approve.save()
            elif colname == 'notify_acknowledgement':
                filepath = after_approve.notify_acknowledgement
                os.remove(filepath.path)
                after_approve.notify_acknowledgement = None
                after_approve.save()
            elif colname == 'card_status':
                filepath = after_approve.card_status
                os.remove(filepath.path)
                after_approve.card_status = None
                after_approve.save()
            messages.success(request, f'{filepath} Deleted..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect(f'/mom-application/after-approval-tep/{id}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AfterApprovedTEPListView(View):
    template_name='after-approved-tep-list.html'
    def get(self, request, passtype=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()
        filter_header_data = str(request.GET.get('filter'))

        if '?keyword' in get_url or '?filter' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        if passtype:
            title="After Approved EP/SPASS List"
        else:
            title="After Approved TEP List"

        if keyword:
            try:
                keyword = datetime.strptime(keyword, '%d/%m/%Y').date()
            except: pass

            if passtype:
                approved_tep = models.AfterApprovalTEPModel.objects.exclude(Q(workpass__epass_type__icontains='tep')
                            ).filter(Q(card_status__isnull=True)
                    |Q(card_status='')).filter(Q(workpass__name__icontains=keyword)|
                    Q(workpass__company_name__company_name__icontains=keyword)|Q(issue__icontains=keyword)|
                    Q(extension_due_20_days__icontains=keyword)|Q(traval_date__icontains=keyword)|
                    Q(thump__icontains=keyword)|Q(new_valid__icontains=keyword)|Q(arived_traval_date__icontains=keyword))
            else:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(card_status__isnull=True)
                    |Q(card_status='')).filter(Q(workpass__name__icontains=keyword)|
                    Q(workpass__company_name__company_name__icontains=keyword)|Q(issue__icontains=keyword)|
                    Q(extension_due_20_days__icontains=keyword)|Q(traval_date__icontains=keyword)|
                    Q(thump__icontains=keyword)|Q(new_valid__icontains=keyword)|Q(arived_traval_date__icontains=keyword)
                    ).filter(workpass__epass_type__icontains='tep').filter(Q(issue__isnull=True)|
                    Q(card_exp__isnull=True)| Q(notify_acknowledgement__isnull=True)|Q(notify_acknowledgement='')
                    ).exclude(workpass__status__icontains='with')
        else:
            if passtype:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(card_status__isnull=True)
                                    |Q(card_status='')).exclude(Q(workpass__epass_type__icontains='tep'))
            else:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(card_status__isnull=True)
                    |Q(card_status='')).filter(workpass__epass_type__icontains='tep').filter(Q(issue__isnull=True)|
                    Q(card_exp__isnull=True)| Q(notify_acknowledgement__isnull=True)|Q(notify_acknowledgement='')
                    ).exclude(workpass__status__icontains='with')

        if 'traval_date' in filter_header_data and 'arived' not in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(traval_date__isnull=False)
            else:
                approved_tep = approved_tep.filter(traval_date__isnull=True)
        elif 'new_valid' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(new_valid__isnull=False)
            else:
                approved_tep = approved_tep.filter(new_valid__isnull=True)
        elif 'extension_due_20_days' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(extension_due_20_days__isnull=False)
            else:
                approved_tep = approved_tep.filter(extension_due_20_days__isnull=True)
        elif 'thump' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(thump__isnull=False)
            else:
                approved_tep = approved_tep.filter(thump__isnull=True)
        elif 'remarks' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(remarks__isnull=False) & ~Q(remarks=''))
            else:
                approved_tep = approved_tep.filter(Q(remarks__isnull=True) | Q(remarks=''))
        elif 'arived_traval_date' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(arived_traval_date__isnull=False)
            else:
                approved_tep = approved_tep.filter(arived_traval_date__isnull=True)
        elif 'issue' in filter_header_data and 'docs' not in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(issue__isnull=False)
            else:
                approved_tep = approved_tep.filter(issue__isnull=True)
        elif 'upload_ipa' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(upload_ipa__isnull=False) & ~Q(upload_ipa=''))
            else:
                approved_tep = approved_tep.filter(Q(upload_ipa__isnull=True)
                                                            |Q(upload_ipa=''))
        elif 'ica_upload' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(ica_upload__isnull=False) & ~Q(ica_upload=''))
            else:
                approved_tep = approved_tep.filter(Q(ica_upload__isnull=True)
                                                            |Q(ica_upload=''))
        elif 'issue_docs' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(issue_docs__isnull=False) & ~Q(issue_docs=''))
            else:
                approved_tep = approved_tep.filter(Q(issue_docs__isnull=True)
                                                            |Q(issue_docs=''))
        elif 'notify_acknowledgement' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(notify_acknowledgement__isnull=False) &
                                                        ~Q(notify_acknowledgement=''))
            else:
                approved_tep = approved_tep.filter(Q(notify_acknowledgement__isnull=True)
                                                            |Q(notify_acknowledgement=''))
        elif 'card_status' in filter_header_data:
            if 'data' in filter_header_data:
                approved_tep = approved_tep.filter(Q(card_status__isnull=False) & ~Q(card_status=''))
            else:
                approved_tep = approved_tep.filter(Q(card_status__isnull=True)
                                                            |Q(card_status=''))

        approved_page = Paginator(approved_tep, 25)
        page_number = request.GET.get('page')
        try:
            approved_page = approved_page.get_page(page_number)
        except PageNotAnInteger:
            approved_page = approved_page.page(1)
        except EmptyPage:
            approved_page = approved_page.page(approved_page.num_pages)
        datas = {'approved_tep': approved_page,
                 'current_url': current_url,
                 'keyword': keyword,
                 'result_cnt': approved_tep.count(),
                 'title': title,
                 'return_url': url_encode_func(request.get_full_path()),}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteApprovedTEP(View):
    def get(self, request, id):
        try:
            approved_tep = models.AfterApprovalTEPModel.objects.get(id=id)
            approved_tep.delete()
            messages.success(request, f'RowID: {id} Deleted..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/mom-application/after-approved-tep-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AfterIssuanceTEPView(View):
    template_name = 'after-issuance-tep.html'
    def get(self, request, passtype=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url or '?filter' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        if passtype:
            title="After Issuance EP/SPASS List"
        else:
            title="After Issuance TEP List"

        if keyword:
            try:
                keyword = datetime.strptime(keyword, '%d/%m/%Y').date()
            except: pass
            if passtype:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(card_status__isnull=False)
                    & ~Q(card_status='')).filter(Q(workpass__name__icontains=keyword)|
                    Q(workpass__source__icontains=keyword)|Q(issue__icontains=keyword)|
                    Q(thump__icontains=keyword)|Q(card_exp__icontains=keyword)).exclude(
                    Q(workpass__epass_type__icontains='tep'))
            else:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(workpass__name__icontains=keyword)|
                    Q(workpass__source__icontains=keyword)|Q(issue__icontains=keyword)|
                    Q(thump__icontains=keyword)|Q(card_exp__icontains=keyword)).filter(
                    workpass__epass_type__icontains='tep').filter(Q(issue__isnull=False) &
                    Q(card_exp__isnull=False))
        else:
            if passtype:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(Q(card_status__isnull=False)
                            & ~Q(card_status='')).exclude(Q(workpass__epass_type__icontains='tep'))
            else:
                approved_tep = models.AfterApprovalTEPModel.objects.filter(
                    workpass__epass_type__icontains='tep').filter(Q(issue__isnull=False) &
                    Q(card_exp__isnull=False))
        approved_page = Paginator(approved_tep, 25)
        page_number = request.GET.get('page')
        try:
            approved_page = approved_page.get_page(page_number)
        except PageNotAnInteger:
            approved_page = approved_page.page(1)
        except EmptyPage:
            approved_page = approved_page.page(approved_page.num_pages)
        datas = {
            'approved_tep': approved_page,
            'current_url': current_url,
            'keyword': keyword,
            'title': title,
            'result_cnt': approved_tep.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

class MOMLiveStatusCheck:
    def __init__(self):
        api_key = "ed577bb6602bd92c6b08d8f873b7e68b"
        self.solver = TwoCaptcha(api_key)

    def captcha_solver(self, site_key):
        result = self.solver.recaptcha(sitekey=site_key,
                    url='https://service2.mom.gov.sg/workpass/ep/api/foreigner/non-login/get-foreigner',)
        self.balance = self.solver.balance()//0.00299
        return result, self.balance

    def check_status(self, datas):
        url = "https://service2.mom.gov.sg/workpass/ep/api/foreigner/non-login/get-foreigner"
        try:
            captcha = self.captcha_solver(datas['site_key'])
            payload = {"searchType":"TRAVDOCNO",
                    "fin":None,
                    "travDocNo": datas['objects']['passport_no'],
                    "dob": datas['objects']['dob'],
                    "doa":"",
                    "recaptchaToken": captcha[0]['code'],
                    }
            res = requests.post(url, data=payload)
            results = res.json()
            results['passport_no'] = datas['objects']['passport_no']
            results['balance'] = captcha[1]
            return results
        except Exception:
            return

def epol_status_check_api(request, id):
    wp = models.WorkPassModel.objects.get(id=id)
    datas = {'site_key': "6LcUZ3YUAAAAAOWMbxLYrNiFEDnRqk-BgKWqj4gu",
            'objects': {
                'passport_no': wp.passport_no, 'dob': wp.dob.strftime('%d %B %Y')
            }}
    check_live = MOMLiveStatusCheck()
    result = check_live.check_status(datas)
    current_date = datetime.today()
    if result is not None:
        try:
            if result.get('success') and type(result.get('results')) == dict:
                wp.status = result['results']['cardData'][0]['cardStatus']
                wp.last_update = current_date
                wp.save()
            else:
                wp.error = True
                wp.status = result['results']
                wp.save()
        except: pass

    try:
        row_cnt = models.CaptchaIssueModel.objects.count()
        if row_cnt == 0:
            sm = models.CaptchaIssueModel(last_update=current_date, balance=check_live.balance)
            sm.save()
        else:
            sm = models.CaptchaIssueModel.objects.last()
            sm.last_update = current_date
            sm.balance = check_live.balance
            sm.save()
    except Exception:
        pass
    try:
        wp = models.WorkPassModel.objects.get(id=id)
        return JsonResponse({'status': wp.status})
    except:
        return JsonResponse({'error': 1})

def create_app_queue_api(request, id=None, return_url=None):
    if request.method == 'POST':
        app_date = request.POST.get('date')
        passtype = request.POST.get('passtype')
        assigned_by = request.POST.get('assigned-by')
        status = request.POST.get('status')
        company = request.POST.get('company')
        emp_ref = request.POST.get('emp-ref')
        staff_name = request.POST.get('staff')
        upload_docs = request.FILES.getlist('file[]')
        voice_record = request.FILES.get('audio')

        try:
            app_date = datetime.strptime(app_date, '%d/%m/%Y')
        except:
            app_date = None
        if id:
            try:
                company = AddCompanyModel.objects.get(id=company)
                if emp_ref == 'Not Applicable':
                    emp_ref = None
                else:
                    emp_ref = AgentManagementCandidataFormModel.objects.get(id=emp_ref)
                edit_app = models.CreateApplicationQueueModel.objects.get(id=id)
                edit_app.app_date=app_date
                edit_app.passtype=passtype
                edit_app.assigned_by=assigned_by
                edit_app.status=status
                edit_app.company=company
                edit_app.employee_ref=emp_ref
                edit_app.staff=staff_name
                if voice_record:
                    edit_app.voice_record = voice_record
                edit_app.save()
                if upload_docs:
                    edit_app.upload_docs.clear()
                    for doc in upload_docs:
                        attach = models.ApplicationQueueFiles(attachments=doc)
                        attach.save()
                        edit_app.upload_docs.add(attach)
                return_url = url_encode_func(return_url, encode=False)
                messages.success(request, f'Application ID : {id} Updated..')
                response_data = {'status': 'success', 'msg': f'Application ID : {id} Updated..',
                                    'return_url': str(return_url)}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'success', 'msg': str(e),
                                    'return_url': '/mom-application/create-app-queue'}
            return JsonResponse(response_data)
        else:
            try:
                company = AddCompanyModel.objects.get(id=company)
                if emp_ref == 'Not Applicable':
                    emp_ref = None
                else:
                    emp_ref = AgentManagementCandidataFormModel.objects.get(id=emp_ref)
                create_app = models.CreateApplicationQueueModel(app_date=app_date, passtype=passtype,
                            assigned_by=assigned_by, status=status, company=company,employee_ref=emp_ref,
                            staff=staff_name, voice_record=voice_record)
                create_app.save()

                for doc in upload_docs:
                    attach = models.ApplicationQueueFiles(attachments=doc)
                    attach.save()
                    create_app.upload_docs.add(attach)
                messages.success(request, 'New Application Created..')
                response_data = {'status': 'success', 'msg': 'New Application Created..'}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e)}
            return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateApplicationQueueView(View):
    template_name='create-app-queue.html'
    def get(self, request, id=None, return_url=None):
        companies=AddCompanyModel.objects.all()
        candidates = AgentManagementCandidataFormModel.objects.all()
        datas = {
            'companies': companies,
            'candidates': candidates,
        }
        if id:
            try:
                edit_app_queue=models.CreateApplicationQueueModel.objects.get(id=id)
                datas['edit_app_queue']=edit_app_queue
                datas['return_url']=return_url
                datas['edit_app_queue_date']=edit_app_queue.app_date.strftime('%d/%m/%Y')
            except:
                pass
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ApplicationQueueListView(View):
    template_name='app-queue-list.html'
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
            app_queues = models.CreateApplicationQueueModel.objects.filter(Q(company__company_name__icontains=keyword)|
                        Q(passtype__icontains=keyword)|Q(employee_ref__icontains=keyword)|
                        Q(assigned_by__icontains=keyword)|Q(staff__icontains=keyword)|Q(status__icontains=keyword)).order_by('-app_date')
        else:
            app_queues = models.CreateApplicationQueueModel.objects.all().order_by('-app_date')
        app_queues_page = Paginator(app_queues, 25)
        page_number = request.GET.get('page')
        try:
            app_queues_page = app_queues_page.get_page(page_number)
        except PageNotAnInteger:
            app_queues_page = app_queues_page.page(1)
        except EmptyPage:
            app_queues_page = app_queues_page.page(app_queues_page.num_pages)
        datas = {
            'app_queues': app_queues_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': app_queues.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteAppQueueView(View):
    def get(self, request, id, return_url):
        try:
            app_queue = models.CreateApplicationQueueModel.objects.get(id=id)
            app_queue.delete()
            messages.success(request, f'Application ID : {id} Deleted..')
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                return redirect('/mom-application/app-queue-list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/mom-application/app-queue-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CustomerEntryForm1API(View):
    def post(self, request, id=None, return_url=None):
        ic_number = request.POST.get('ic-number')
        dob = request.POST.get('dob')
        name = request.POST.get('name')
        nationality = request.POST.get('nationality')
        refer_by = request.POST.get('refer-by')
        contact_number = request.POST.get('contact-number') if request.POST.get('contact-number') else None
        ic_copy_file = request.FILES.get('ic-copy-file')

        try:
            dob = datetime.strptime(dob, '%d/%m/%Y')
        except:
            dob = None

        if id:
            try:
                refer_by = NewClientModel.objects.get(id=refer_by)
                customer_entry_form1 = models.CustomerEntryForm1Model.objects.get(id=id)
                customer_entry_form1.ic_number = ic_number
                customer_entry_form1.dob = dob
                customer_entry_form1.name = name
                customer_entry_form1.nationality = nationality
                customer_entry_form1.referby = refer_by
                customer_entry_form1.contact_number = contact_number
                if ic_copy_file:
                    customer_entry_form1.ic_copy_file = ic_copy_file
                customer_entry_form1.save()
                messages.success(request, f'Customer {name} Updated..')
                return_url = url_encode_func(return_url, encode=False)
                response_data = {'status': 'success', 'msg': f'Customer {name} Updated..',
                                 'return_url': str(return_url)}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e),
                                 'return_url': '/mom-application/cpf-entry-form1'}
        else:
            try:
                refer_by = NewClientModel.objects.get(id=refer_by)
                customer_entry_form1 = models.CustomerEntryForm1Model(
                    ic_number=ic_number, dob=dob, name=name, nationality=nationality, referby=refer_by,
                    contact_number=contact_number, ic_copy_file=ic_copy_file
                )
                customer_entry_form1.save()
                messages.success(request, f'New Customer {name} Created..')
                response_data = {'status': 'success', 'msg': f'New Customer {name} Created..'}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e)}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFEntryForm1View(View):
    template_name='entry-form1.html'
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
            entry_form1_datas = models.CustomerEntryForm1Model.objects.filter(
                Q(ic_number__icontains=keyword)|Q(name__icontains=keyword)|Q(dob__icontains=keyword)|
                Q(nationality__icontains=keyword)|Q(referby__client_name__icontains=keyword)|
                Q(contact_number__icontains=keyword)
            )
        else:
            entry_form1_datas = models.CustomerEntryForm1Model.objects.all()

        clients = NewClientModel.objects.all()

        entry_form1_datas_page = Paginator(entry_form1_datas, 25)
        page_number = request.GET.get('page')
        try:
            entry_form1_datas_page = entry_form1_datas_page.get_page(page_number)
        except PageNotAnInteger:
            entry_form1_datas_page = entry_form1_datas_page.page(1)
        except EmptyPage:
            entry_form1_datas_page = entry_form1_datas_page.page(entry_form1_datas_page.num_pages)
        datas = {
            'clients': clients,
            'entry_form1_datas': entry_form1_datas_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': entry_form1_datas.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFEntryForm1UpdateView(View):
    template_name='entry-form1-update.html'
    def get(self, request, id, return_url):
        clients = NewClientModel.objects.all()
        entry_form1_datas = models.CustomerEntryForm1Model.objects.all()
        datas = {
            'clients': clients,
            'entry_form1_datas': entry_form1_datas,
            'return_url': return_url,
        }
        if id:
            try:
                edit_entry_form = models.CustomerEntryForm1Model.objects.get(id=id)
                datas['edit_entry_form'] = edit_entry_form
                datas['edit_entry_form_dob']=edit_entry_form.dob.strftime('%d/%m/%Y')
            except: pass
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteEnterForm1View(View):
    def get(self, request, id, return_url):
        try:
            entry_form = models.CustomerEntryForm1Model.objects.get(id=id)
            entry_form.delete()
            messages.success(request, f'CustomerID : {id} Deleted..')
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                return redirect('/mom-application/cpf-entry-form1')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/mom-application/cpf-entry-form1')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFEntryForm2View(View):
    template_name='entry-form2.html'
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
            entry_form2_datas = models.CustomerEntryForm2Model.objects.filter(
                Q(month_year__icontains=keyword)|Q(no_of_fulltime__icontains=keyword)|
                Q(no_of_parttime__icontains=keyword)|Q(company_name__company_name__icontains=keyword)|
                Q(declaration__icontains=keyword)
            )
        else:
            entry_form2_datas = models.CustomerEntryForm2Model.objects.all()

        companies = AddCompanyModel.objects.all()

        entry_form2_datas_page = Paginator(entry_form2_datas.order_by('-month_year'), 25)
        page_number = request.GET.get('page')
        try:
            entry_form2_datas_page = entry_form2_datas_page.get_page(page_number)
        except PageNotAnInteger:
            entry_form2_datas_page = entry_form2_datas_page.page(1)
        except EmptyPage:
            entry_form2_datas_page = entry_form2_datas_page.page(entry_form2_datas_page.num_pages)
        datas = {
            'companies': companies,
            'entry_form2_datas': entry_form2_datas_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': entry_form2_datas.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CustomerEntryForm2API(View):
    def post(self, request, id=None, return_url=None):
        company = request.POST.get('company')
        fulltime = request.POST.get('fulltime') if request.POST.get('fulltime') else 0
        month_year = request.POST.get('month_year')
        parttime = request.POST.get('parttime') if request.POST.get('parttime') else 0
        declaration = request.POST.get('declaration')
        draft_upload = request.FILES.get('draft_upload')

        try:
            month_year = datetime.strptime(f'{month_year}-1', '%Y-%m-%d')
        except:
            month_year = None

        if id:
            try:
                company = AddCompanyModel.objects.get(id=company)
                customer_entry_form2 = models.CustomerEntryForm2Model.objects.get(id=id)
                customer_entry_form2.company_name = company
                customer_entry_form2.month_year = month_year
                customer_entry_form2.no_of_fulltime = fulltime
                customer_entry_form2.no_of_parttime = parttime
                customer_entry_form2.declaration = declaration
                if draft_upload:
                    customer_entry_form2.draft_upload = draft_upload
                customer_entry_form2.save()
                messages.success(request, f'{company.company_name} Updated..')
                return_url = url_encode_func(return_url, encode=False)
                response_data = {'status': 'success', 'msg': f'{company.company_name} Updated..',
                                 'return_url': str(return_url)}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e),
                                 'return_url': '/mom-application/cpf-entry-form2'}
        else:
            try:
                company = AddCompanyModel.objects.get(id=company)
                customer_entry_form2 = models.CustomerEntryForm2Model(
                    company_name=company, month_year=month_year, no_of_fulltime=fulltime, no_of_parttime=parttime,
                    declaration=declaration, draft_upload=draft_upload
                )
                customer_entry_form2.save()
                messages.success(request, f'{company} Created..')
                response_data = {'status': 'success', 'msg': f'{company} Created..'}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e)}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFEntryForm2UpdateView(View):
    template_name='entry-form2-update.html'
    def get(self, request, id, return_url):
        companies = AddCompanyModel.objects.all()
        entry_form2_datas = models.CustomerEntryForm2Model.objects.all()
        datas = {
            'companies': companies,
            'entry_form2_datas': entry_form2_datas,
            'return_url': return_url,
        }
        if id:
            try:
                edit_entry_form = models.CustomerEntryForm2Model.objects.get(id=id)
                datas['edit_entry_form'] = edit_entry_form
                datas['edit_entry_form_my']=edit_entry_form.month_year.strftime('%Y-%m')
            except: pass
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteEnterForm2View(View):
    def get(self, request, id, return_url):
        try:
            entry_form = models.CustomerEntryForm2Model.objects.get(id=id)
            entry_form.delete()
            messages.success(request, f'CustomerID : {id} Deleted..')
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                return redirect('/mom-application/cpf-entry-form2')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/mom-application/cpf-entry-form2')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFEntryReportListView(View):
    template_name='entry-report.html'
    def get(self, request):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        companies = models.AddCompanyModel.objects.all().order_by('client__client_id', 'company_id')
        companies_page = Paginator(companies, 25)
        page_number = request.GET.get('page')
        try:
            companies_page = companies_page.get_page(page_number)
        except PageNotAnInteger:
            companies_page = companies_page.page(1)
        except EmptyPage:
            companies_page = companies_page.page(companies_page.num_pages)

        datas = {
            'current_year': str(datetime.today().year)[-2:],
            'companies_page': companies_page,
            'current_url': current_url,
        }
        return render(request, self.template_name, context=datas)
