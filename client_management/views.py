from django.shortcuts import render, redirect
from django.views import View
from client_management import models
from django.contrib import messages
from django.db.models import Q, Count
import xlsxwriter, re, base64, openpyxl, random
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from mom_application.models import AfterApprovalTEPModel, WorkPassModel
import logging, dropbox, pyshorteners
from pydub import AudioSegment
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from pydub.utils import which
AudioSegment.converter = which("ffmpeg")

db_logger = logging.getLogger('db')

def url_encode_func(url, encode=True):
    if encode:
        return base64.urlsafe_b64encode(url.encode()).decode()
    return base64.urlsafe_b64decode(url.encode()).decode()

@method_decorator(login_required(login_url="/"), name='dispatch')
class NewClientView(View):
    template_name = 'new-client.html'
    def get(self, request, id=None):
        datas = {}
        if id is not None:
            datas['client'] = models.NewClientModel.objects.get(id=id)
        return render(request, self.template_name, context=datas)

    def post(self, request, id=None):
        client_name = request.POST.get('client-name')
        phone = request.POST.get('phone')

        if phone == '':
            phone = None

        if id is None:
            try:
                client_cnt = models.NewClientModel.objects.count()
                if client_cnt == 0:
                    ccnt = 1
                else:
                    last_client = models.NewClientModel.objects.last()
                    ccnt = last_client.client_id + 1

                client = models.NewClientModel(client_id=ccnt, client_name=client_name,
                                phone_number=phone)
                client.save()
                messages.info(request, f'New Client: {client_name} Added..')
            except Exception as e:
                messages.info(request, f'Error: {e}')
        else:
            try:
                client = models.NewClientModel.objects.get(id=id)
                client.client_name = client_name
                client.phone_number = phone
                client.save()
                messages.info(request, f'Client: {client_name} Updated..')
            except Exception as e:
                messages.info(request, f"Error: {e}")
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed New Client Page')
        return redirect('/client-management/new-client')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AddCompanyView(View):
    template_name = 'add-company.html'

    def col_to_num(self, col_str):
        expn = 0
        col_num = 0
        for char in reversed(col_str):
            col_num += (ord(char) - ord('A') + 1) * (26 ** expn)
            expn += 1
        return col_num

    def company_id(self, client, comp):
        company = models.AddCompanyModel.objects.filter(client=client).count()
        if company != 0:
            comp = models.AddCompanyModel.objects.filter(client=client).last()
            company = self.col_to_num(re.sub('[0-9]+', '', comp.company_id))
        return f"{client.client_id}{xlsxwriter.utility.xl_col_to_name(company)}"

    def get(self, request, id=None):
        datas = {}
        clients = models.NewClientModel.objects.all()
        datas['clients'] = clients
        if id is not None:
            try:
                edit_client = models.AddCompanyModel.objects.get(id=id)
                datas['edit_client'] = edit_client
                datas['finance_year_end'] = edit_client.company_review.finance_year_end
                datas['date_of_incorp'] = edit_client.company_review.date_of_incorp
            except: pass
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Company Page')
        return render(request, self.template_name, context=datas)

    def post(self, request, id=None):
        client_id = request.POST.get('client')
        roc = request.POST.get('roc')
        contact_person = request.POST.get('contact-person') if request.POST.get('contact-person') else None
        singpass_qr = request.POST.get('singpass')
        comp_name = request.POST.get('comp-name')
        email = request.POST.get('email') if request.POST.get('email') else None
        contact_number = request.POST.get('contact-number') if request.POST.get('contact-number') else None
        singpass_id = request.POST.get('singpass-id') if request.POST.get('singpass-id') else None
        singpass_password = request.POST.get('singpass-password') if request.POST.get('singpass-password') else None
        director_name = request.POST.get('director-name')
        date_of_incorp = request.POST.get('date-of-incorp')
        fin_year_end = request.POST.get('fin-year-end')
        if id is None:
            try:
                if models.AddCompanyModel.objects.filter(company_name=comp_name, roc=roc):
                    messages.error(request, f'{comp_name} {roc} => Company Name & ROC Number Already Exists!!!')
                    return redirect('/client-management/add-company')
                client_name = models.NewClientModel.objects.get(id=int(client_id))
                singpass_qr = True if 'qr-code' == singpass_qr else False
                get_company_id = self.company_id(client_name, comp_name)
                company = models.AddCompanyModel(client=client_name, company_id=get_company_id, company_name=comp_name, roc=roc,
                            email=email, contact_person=contact_person, contact_number=contact_number,
                            singpass_id=singpass_id, singpass_password=singpass_password, qr_code=singpass_qr,
                            director_name=director_name)
                company.save()
                try:
                    review_form = models.CompanyReviewModel(date_of_incorp=date_of_incorp,
                                                            finance_year_end=fin_year_end)
                    review_form.save()
                    company.company_review = review_form
                    company.save()
                except: pass
                messages.success(request, f'New Client {client_name.client_name} Added..')
            except Exception as e:
                messages.error(request, f'{e}')
        else:
            try:
                client_name = models.NewClientModel.objects.get(id=int(client_id))
                singpass_qr = True if 'qr-code' == singpass_qr else False
                company = models.AddCompanyModel.objects.get(id=id)
                company.client = client_name
                company.company_name = comp_name
                company.roc = roc
                company.contact_person = contact_person
                company.email = email
                company.contact_number = contact_number
                company.singpass_id = singpass_id
                company.singpass_password = singpass_password
                company.qr_code = singpass_qr
                company.director_name = director_name
                company.save()

                comp_review = company.company_review
                comp_review.finance_year_end = fin_year_end
                comp_review.date_of_incorp = date_of_incorp
                comp_review.save()
                messages.success(request, f'Client: {client_name.client_name} Updated..')
            except Exception as e:
                messages.error(request, f'Error: {e}')

        return redirect('/client-management/add-company')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CompanyListView(View):
    template_name = 'companies-list.html'
    def get(self, request):
        keyword = request.GET.get('keyword')

        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        if keyword is not None:
            clients = models.AddCompanyModel.objects.filter(Q(client__client_name__icontains=keyword) |
                        Q(company_name__icontains=keyword) |
                        Q(roc__icontains=keyword) | Q(company_id__icontains=keyword) |
                        Q(client__phone_number__icontains=keyword)).order_by('client__client_id', 'company_id')
        else:
            clients = models.AddCompanyModel.objects.all().order_by('client__client_id', 'company_id')

        clients_page = Paginator(clients, 15)
        page_number = request.GET.get('page')

        try:
            clients_page = clients_page.get_page(page_number)
        except PageNotAnInteger:
            clients_page = clients_page.page(1)
        except EmptyPage:
            clients_page = clients_page.page(clients_page.num_pages)

        datas = {
            # 'clients': clients,
            'current_url': current_url,
            'clients_page': clients_page,
            'result_cnt': clients.count(),
            'keyword': keyword,
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Company List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CompanyDeleteView(View):
    def get(self, request, id, page=None):
        try:
            company = models.AddCompanyModel.objects.get(id=id)
            client_id = company.client.id
            comp_id = f"{company.company_id}-{company.company_name}"
            company.delete()
            messages.info(request, f'CompanyID - {comp_id} Deleted..')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {comp_id} Company')
            if page is not None:
                return redirect(f'/client-management/view-client-companies/{client_id}')
        except Exception as e:
            messages.info(request, f'{e}')

        return redirect('/client-management/companies-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class ClientsListView(View):
    template_name = 'clients-list.html'
    def get(self, request):
        keyword = request.GET.get('keyword')

        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        if keyword is not None:
            clients = models.NewClientModel.objects.filter(Q(client_name__icontains=keyword) |
                        Q(phone_number__icontains=keyword))
        else:
            clients = models.NewClientModel.objects.all().order_by('client_id')

        clients_page = Paginator(clients, 15)
        page_number = request.GET.get('page')

        try:
            clients_page = clients_page.get_page(page_number)
        except PageNotAnInteger:
            clients_page = clients_page.page(1)
        except EmptyPage:
            clients_page = clients_page.page(clients_page.num_pages)

        datas = {
            'clients_page': clients_page,
            'keyword': keyword,
            'current_url': current_url,
            'result_cnt': clients.count(),
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Clients List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ClientDeleteView(View):
    def get(self, request, id):
        try:
            client = models.NewClientModel.objects.get(id=id)
            cid, cname = client.client_id, client.client_name
            client.delete()
            messages.info(request, f'Client : {cid}-{cname} Deleted..')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {cname} Client')
        except Exception as e:
            messages.info(request, f'{e}')

        return redirect('/client-management/clients-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class ViewClientView(View):
    template_name = 'view-client.html'
    def get(self, request, id):
        client = models.NewClientModel.objects.get(id=id)
        companies = models.AddCompanyModel.objects.filter(client=client)
        datas = {
            'companies': companies,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ViewClientCompaniesView(View):
    template_name = 'client-companies-list.html'
    def get(self, request, id):
        try:
            client = models.NewClientModel.objects.get(id=id)
            companies = models.AddCompanyModel.objects.filter(client=client)
            datas = {'clients_page': companies}
        except:
            return redirect('/client-management/clients-list')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ViewCompanyDeleteView(View):
    def get(self, request, id, client_id):
        try:
            company = models.AddCompanyModel.objects.get(id=id)
            comp_id = f"{company.company_id}-{company.company_name}"
            company.delete()
            messages.info(request, f'CompanyID - {comp_id} Deleted..')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {comp_id} Company')
        except Exception as e:
            messages.info(request, f'{e}')

        return redirect(f'/client-management/view-client/{client_id}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CompanyReviewFormView(View):
    template_name = 'company-review-form.html'
    def get(self, request, id, page, return_url):
        try:
            select_company = models.AddCompanyModel.objects.get(id=id)
            datas = {'select_company': select_company,
                    'return_url': url_encode_func(request.get_full_path()),}
            try:
                status_date = select_company.company_review.status_date.strftime('%Y-%m-%d')
                datas['edit_status_date'] = status_date
            except: pass

        except Exception:
            datas = {'return_url': url_encode_func(request.get_full_path()),}
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Company Review Form')
        return render(request, self.template_name, context=datas)

    def post(self, request, id, page, return_url):
        status_date = request.POST.get('status_date')
        status = request.POST.get('status')
        local_col = request.POST.get('local_col')
        new_sfa = request.POST.get('new_sfa')
        new_sp = request.POST.get('new_sp') if request.POST.get('new_sp') else 0
        new_wp = request.POST.get('new_wp') if request.POST.get('new_wp') else 0
        new_prc = request.POST.get('new_prc') if request.POST.get('new_prc') else 0
        new_ind = request.POST.get('new_ind') if request.POST.get('new_ind') else 0
        try:
            status_date = datetime.strptime(status_date, '%Y-%m-%d')
        except Exception:
            status_date = None

        try:
            company = models.AddCompanyModel.objects.get(id=id)
        except Exception:
            company = None

        try:
            if company.company_review is not None:
                review_form = models.CompanyReviewModel.objects.get(id=company.company_review.id)
                review_form.status_date = status_date
                review_form.local_col = local_col
                review_form.new_sfa = new_sfa
                review_form.status = status
                review_form.new_sp = new_sp
                review_form.new_wp = new_wp
                review_form.new_prc = new_prc
                review_form.new_ind = new_ind
                review_form.save()
                messages.success(request, f'Company: {company.company_id}-{company.company_name} Info Added')
                try:
                    return_url = url_encode_func(return_url, encode=False)
                    return redirect(return_url)
                except:
                    return redirect(f'/client-management/company-review-list?page={page}')

            review_form = models.CompanyReviewModel(status_date=status_date,
                            status=status, local_col=local_col, new_sfa=new_sfa, new_sp=new_sp, new_wp=new_wp,
                            new_prc=new_prc, new_ind=new_ind)
            review_form.save()
        except Exception as e:
            messages.error(request, f'Error: {e}!!!')
            try:
                return_url = url_encode_func(return_url, encode=False)
                return redirect(return_url)
            except:
                return redirect(f'/client-management/company-review-list?page={page}')
        try:
            company.company_review = review_form
            company.save()
            messages.success(request, f'Company: {company.company_id}-{company.company_name} Info Added')
        except Exception as e:
            messages.error(request, f'Error: {e}!!!')

        try:
            return_url = url_encode_func(return_url, encode=False)
            return redirect(return_url)
        except:
            return redirect(f'/client-management/company-review-list?page={page}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CompanyReviewListView(View):
    template_name='company-review-list.html'
    def get(self, request):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        sfa_cnt = models.AddCompanyModel.objects.filter(company_review__new_sfa__isnull=False).exclude(company_review__new_sfa='')
        note_cnt = models.AddCompanyModel.objects.filter(company_review__note__isnull=False).exclude(company_review__note='')
        new_sp_cnt = models.AddCompanyModel.objects.filter(company_review__new_sp__isnull=False
                                            ).exclude(Q(company_review__new_sp=0)|Q(company_review__new_sp__iexact='no'))
        new_wp_cnt = models.AddCompanyModel.objects.filter(company_review__new_wp__isnull=False
                                            ).exclude(Q(company_review__new_wp=0)|Q(company_review__new_wp__iexact='no'))
        new_prc_cnt = models.AddCompanyModel.objects.filter(company_review__new_prc__isnull=False
                                            ).exclude(Q(company_review__new_prc=0)|Q(company_review__new_prc__iexact='no'))
        new_ind_cnt = models.AddCompanyModel.objects.filter(company_review__new_ind__isnull=False
                                            ).exclude(Q(company_review__new_ind=0)|Q(company_review__new_ind__iexact='no'))
        if keyword is not None:
            if keyword.lower().startswith('emp='):
                try:
                    emp = int(keyword.split('=')[-1])
                    review_lists = models.AddCompanyModel.objects.filter(client__client_id=emp)
                except:
                    review_lists = models.AddCompanyModel.objects.all()
            elif keyword == f'sfa:{sfa_cnt.count()}':
                review_lists = sfa_cnt
            elif keyword == f'note:{note_cnt.count()}':
                review_lists = note_cnt
            elif keyword == f'new_sp:{new_sp_cnt.count()}':
                review_lists = new_sp_cnt
            elif keyword == f'new_wp:{new_wp_cnt.count()}':
                review_lists = new_wp_cnt
            elif keyword == f'new_prc:{new_prc_cnt.count()}':
                review_lists = new_prc_cnt
            elif keyword == f'new_ind:{new_ind_cnt.count()}':
                review_lists = new_ind_cnt
            else:
                review_lists = models.AddCompanyModel.objects.filter(Q(company_name__icontains=keyword) |
                        Q(company_id__icontains=keyword)|Q(roc__icontains=keyword))
        else:
            review_lists = models.AddCompanyModel.objects.all()
        review_lists = sorted(review_lists, key=lambda data: data.client.client_id)
        review_page = Paginator(review_lists, 15)
        page_number = request.GET.get('page')
        try:
            review_page = review_page.get_page(page_number)
        except PageNotAnInteger:
            review_page = review_page.page(1)
        except EmptyPage:
            review_page = review_page.page(review_page.num_pages)
        datas = {
            'review_lists': review_page,
            'keyword': keyword,
            'current_url': current_url,
            'result_cnt': review_lists.count() if type(review_lists) != list else len(review_lists),
            'sfa_cnt': sfa_cnt.count(),
            'note_cnt': note_cnt.count(),
            'new_sp_cnt': new_sp_cnt.count(),
            'new_wp_cnt': new_wp_cnt.count(),
            'new_prc_cnt': new_prc_cnt.count(),
            'new_ind_cnt': new_ind_cnt.count(),
            'return_url': url_encode_func(request.get_full_path()),
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Company Review List')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CompanyReviewNoteView(View):
    template_name='company-review-note.html'
    def get(self, request, id, page):
        try:
            comp = models.AddCompanyModel.objects.get(id=id)
            datas = {'comp': comp}
        except:
            datas = {}
        return render(request, self.template_name, context=datas)
    def post(self, request, id, page):
        note = request.POST.get('note')
        try:
            note = note.strip()
            comp = models.AddCompanyModel.objects.get(id=id)
            if comp.company_review:
                cr = models.CompanyReviewModel.objects.get(id=comp.company_review.id)
                cr.note = note
                cr.save()
            else:
                cr = models.CompanyReviewModel(note=note)
                cr.save()
                comp.company_review = cr
                comp.save()
            messages.success(request, f'{comp.company_name}, Note Updated..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect(f'/client-management/company-review-list?page={page}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateOrderView(View):
    template_name = 'create-order-form.html'
    def change_pitch(self, sound, octaves):
        new_sample_rate = int(sound.frame_rate * (0.8 ** octaves))
        return sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(sound.frame_rate)

    def change_speed(self, sound, factor):
        return sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * factor)
        }).set_frame_rate(sound.frame_rate)

    def process_audio(self, audio_bytes, pitch_change, speed_change):
        audio = AudioSegment.from_file(audio_bytes)
        modified_audio = self.change_pitch(audio, pitch_change)
        modified_audio = self.change_speed(modified_audio, speed_change)

        out_bytes = BytesIO()
        modified_audio.export(out_bytes, format="mp3")
        out_bytes.seek(0)
        return out_bytes.getvalue()

    def upload_audio_file(self, file, filename):
        try:
            token = 'sl.B3WP88dy2ci_b84fEtL2HF_VKVWwBTCogSN15h8Iwv7lXwtS_OuMZa-50YC39ibOxcQ1bklNv8gWnSevhn87uJzMox0MJwy4yyuqySwTwzTctQiy47JNtmnzRkwJHzsQ9aO69Y6rTUcYvJ2SR3cbeUA'
            dbx = dropbox.Dropbox(token)
            data = dbx.files_upload(file, f'/{filename}')
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(data.path_display)
            return shared_link_metadata.url
        except:
            return None

    def shorten_url(self, long_url):
        s = pyshorteners.Shortener()
        return s.tinyurl.short(long_url)

    def generate_refid(self, ordermodel, compid):
        comp = models.AddCompanyModel.objects.get(id=compid)
        if comp.create_orderid_track:
            backupid = comp.create_orderid_track.get(str(compid), 0)
            backupid = str(backupid)
            backupid = backupid[::-1]
            r = ''
            for i in backupid:
                if i.isdigit():
                    r += i
                else:
                    break
            if r:
                r = r[::-1]
                backupid = int(r)
            else:
                backupid = 0
        else:
            backupid = 0

        if ordermodel:
            lastid = str(ordermodel.last().ref_id)
            lastid = lastid[::-1]
            r = ''
            for i in lastid:
                if i.isdigit():
                    r += i
                else:
                    break
            if r:
                r = r[::-1]
                lastid = int(r)
            else:
                lastid = 0
        else:
            if backupid:
                lastid = int(backupid)
            else:
                lastid = 0

        if lastid < backupid:
            return backupid+1
        else:
            return lastid+1

    def get(self, request, id, update_id=None):
        company = models.AddCompanyModel.objects.get(id=id)
        created_order = models.CreateOrderModel.objects.filter(company=company)
        if created_order:
            ref_id = f"{company.company_id}{self.generate_refid(created_order, company.id)}"
        else:
            try:
                ref_id = f"{company.company_id}{self.generate_refid(created_order, company.id)}"
            except:
                ref_id = f'{company.company_id}1'
        datas = {
            'today': datetime.today().date(),
            'selected_comp': company,
            'ref_id': ref_id
        }
        if update_id:
            try:
                create_order_obj = models.CreateOrderModel.objects.get(id=update_id)
                datas['create_order_obj'] = create_order_obj
                datas['today'] = create_order_obj.order_date
                datas['ref_id'] = create_order_obj.ref_id
                try:
                    datas['edit_require_date'] = create_order_obj.require_date.strftime('%Y-%m-%d')
                except: pass
            except Exception as e:
                messages.error(request, f'Error: {e}')
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Create Order Page')
        return render(request, self.template_name, context=datas)

    def post(self, request, id, update_id=None):
        require_date = request.POST.get('require-date')
        pass_type = request.POST.get('pass-type')
        no_of_vac = request.POST.get('no-of-vac')
        description = request.POST.get('description')
        voice = request.FILES.get('audio')
        exist_modified_audio = request.FILES.get("exist-modified-audio")
        try:
            no_of_vac = int(no_of_vac)
        except:
            no_of_vac = 0

        dbx_url, short_url, error1, error2 = None, None, '', ''
        try:
            if voice:
                filename = f'{voice}'
                try:
                    voice = self.process_audio(voice, 1, 1.6)
                    voice = InMemoryUploadedFile(
                                file=BytesIO(voice),
                                field_name=None,
                                name=filename,
                                content_type='audio/mpeg',
                                size=len(voice),
                                charset=None
                            )
                except Exception as e:
                    error1 = f'{e}'
                file = voice.read()
                dbx_url = self.upload_audio_file(file, filename)
                if dbx_url is not None:
                    short_url = self.shorten_url(dbx_url)
        except Exception as e:
            error2 = f'{e}'

        try:
            require_date = datetime.strptime(require_date, '%Y-%m-%d')
        except:
            require_date = None
        try:
            if exist_modified_audio:
                filename = f"{exist_modified_audio}"
                exist_modified_audio = self.process_audio(exist_modified_audio, 1, 1.6)
                exist_modified_audio = InMemoryUploadedFile(
                            file=BytesIO(exist_modified_audio),
                            field_name=None,
                            name=filename,
                            content_type='audio/mpeg',
                            size=len(exist_modified_audio),
                            charset=None
                        )
        except:
            pass

        if update_id:
            try:
                company = models.AddCompanyModel.objects.get(id=id)
                created_order = models.CreateOrderModel.objects.filter(company=company)
                ref_id = f"{company.company_id}{created_order.count()+1}"
                create_order = models.CreateOrderModel.objects.get(id=update_id)
                create_order.company = company
                create_order.description = description
                create_order.pass_type = pass_type
                create_order.no_of_vacancies = no_of_vac
                create_order.require_date = require_date
                if voice:
                    create_order.voice_record = voice
                if exist_modified_audio:
                    create_order.exist_modified_audio = exist_modified_audio
                create_order.dropbox_url = dbx_url
                create_order.tiny_url = short_url
                create_order.save()
                messages.success(request, f'{company.company_name} updated..')
                response_data = {'status': 'success'}
            except Exception as e:
                messages.error(request, f'Error: {e}')
                response_data = {'status': 'error'}
        else:
            try:
                company = models.AddCompanyModel.objects.get(id=id)
                for _ in range(no_of_vac):
                    created_order = models.CreateOrderModel.objects.filter(company=company)
                    ref_id = f"{company.company_id}{self.generate_refid(created_order, company.id)}"

                    create_order = models.CreateOrderModel(ref_id=ref_id, company=company, description=description,
                                        pass_type=pass_type, no_of_vacancies=1, voice_record=voice,
                                        dropbox_url=dbx_url, tiny_url=short_url, require_date=require_date,exist_modified_audio=exist_modified_audio)
                    create_order.save()
                messages.success(request, f'New Order Created - {company.company_name}.')
                response_data = {'status': 'success'}
            except Exception as e:
                messages.error(request, f'Error: {e}. {voice}')
                response_data = {'status': 'error'}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class OrderListView(View):
    template_name='order-list.html'
    def get(self, request, id):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        try:
            if keyword:
                if keyword == 'OTHERS':
                    comp = models.AddCompanyModel.objects.get(id=id)
                    orders = models.CreateOrderModel.objects.filter(company=comp).exclude(
                                    Q(pass_type__istartswith='EP')|Q(pass_type__istartswith='SP')|
                                    Q(pass_type__istartswith='TEP')|Q(pass_type__istartswith='WP')|
                                    Q(pass_type__istartswith='TWP')|Q(pass_type__istartswith='NTS')
                                    ).filter(application_id__isnull=True)
                    # ('EP', 'SP', 'TEP', 'WP', 'NTS')
                else:
                    comp = models.AddCompanyModel.objects.get(id=id)
                    orders = models.CreateOrderModel.objects.filter(company=comp).filter(
                                Q(company__company_name__icontains=keyword)
                                |Q(description__icontains=keyword)|Q(pass_type__istartswith=keyword)|
                                Q(application_id__icontains=keyword)|Q(ref_id__icontains=keyword)
                                ).filter(application_id__isnull=True)
            else:
                orders = models.CreateOrderModel.objects.filter(application_id__isnull=True)
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/client-management/grouped-order-list')
        orders_page = Paginator(orders, 25)
        page_number = request.GET.get('page')
        try:
            orders_page = orders_page.get_page(page_number)
        except PageNotAnInteger:
            orders_page = orders_page.page(1)
        except EmptyPage:
            orders_page = orders_page.page(orders_page.num_pages)
        datas = {
            'orders': orders_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': orders.count(),
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Orders List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class OrderListOverallView(View):
    template_name='order-list-overall.html'
    def get(self, request):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        try:
            if keyword:
                orders = models.CreateOrderModel.objects.filter(
                            Q(company__company_name__icontains=keyword)
                            |Q(description__icontains=keyword)|Q(pass_type__istartswith=keyword)|
                            Q(application_id__icontains=keyword)|Q(ref_id__icontains=keyword)
                            ).filter(application_id__isnull=True).order_by('require_date')
            else:
                orders = models.CreateOrderModel.objects.filter(application_id__isnull=True).order_by('require_date')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/client-management/grouped-order-list')
        orders_page = Paginator(orders, 25)
        page_number = request.GET.get('page')
        try:
            orders_page = orders_page.get_page(page_number)
        except PageNotAnInteger:
            orders_page = orders_page.page(1)
        except EmptyPage:
            orders_page = orders_page.page(orders_page.num_pages)
        datas = {
            'orders': orders_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': orders.count(),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class GroupOrderListView(View):
    template_name='grouped-order-list.html'
    def group_order_list(self, datas):
        result = {}
        for data in datas:
            if result.get(data['company']):
                pcol = data['pass_type'].upper()
                if pcol.startswith('EP'):
                    result[data['company']]['EP'] = result[data['company']][
                                    'EP']+data['pass_type_count']
                elif pcol.startswith('SP'):
                    result[data['company']]['SP'] = result[data['company']][
                                    'SP']+data['pass_type_count']
                elif pcol.startswith('TEP'):
                    result[data['company']]['TEP'] = result[data['company']][
                                    'TEP']+data['pass_type_count']
                elif pcol.startswith('WP'):
                    result[data['company']]['WP'] = result[data['company']][
                                    'WP']+data['pass_type_count']
                elif pcol.startswith('TWP'):
                    result[data['company']]['TWP'] = result[data['company']][
                                    'TWP']+data['pass_type_count']
                elif pcol.startswith('NTS'):
                    result[data['company']]['NTS'] = result[data['company']][
                                    'NTS']+data['pass_type_count']
                else:
                    result[data['company']]['OTHERS'] = result[data['company']][
                                    'OTHERS']+data['pass_type_count']
            else:
                result[data['company']] = {
                    'EP': 0,'SP': 0,'TEP': 0,'WP': 0,'TWP': 0,'NTS': 0,'OTHERS': 0}
                pcol = data['pass_type'].upper()
                if pcol.startswith('EP'):
                    result[data['company']]['EP'] = result[data['company']][
                                    'EP']+data['pass_type_count']
                elif pcol.startswith('SP'):
                    result[data['company']]['SP'] = result[data['company']][
                                    'SP']+data['pass_type_count']
                elif pcol.startswith('TEP'):
                    result[data['company']]['TEP'] = result[data['company']][
                                    'TEP']+data['pass_type_count']
                elif pcol.startswith('WP'):
                    result[data['company']]['WP'] = result[data['company']][
                                    'WP']+data['pass_type_count']
                elif pcol.startswith('TWP'):
                    result[data['company']]['TWP'] = result[data['company']][
                                    'TWP']+data['pass_type_count']
                elif pcol.startswith('NTS'):
                    result[data['company']]['NTS'] = result[data['company']][
                                    'NTS']+data['pass_type_count']
                else:
                    result[data['company']]['OTHERS'] = result[data['company']][
                                    'OTHERS']+data['pass_type_count']
        return result

    def filt_orders(self, datas, k):
        result = {}
        for dk, dv in datas.items():
            if datas[dk][k]:
                result[dk] = dv
        return result

    def get(self, request, order_key=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"
        if keyword:
            orders = models.CreateOrderModel.objects.filter(application_id__isnull=True,
                    ).filter(Q(company__company_name__icontains=keyword) | Q(company__roc__icontains=keyword)).values(
                    'company', 'pass_type').annotate(pass_type_count=Count('pass_type')).order_by(
                    'company__client__client_id', 'company__company_id')
        else:
            orders = models.CreateOrderModel.objects.filter(application_id__isnull=True).values(
                'company', 'pass_type').annotate(
                    pass_type_count=Count('pass_type')).order_by('company__client__client_id', 'company__company_id')
        try:
            orders_list = self.group_order_list(orders)
        except:
            orders_list = {}

        tot_cnts = {'EP': 0, 'SP': 0, 'TEP': 0, 'WP': 0, 'TWP': 0, 'NTS': 0, 'OTHERS': 0}
        for d in orders_list.values():
            tot_cnts['EP'] += d.get('EP', 0)
            tot_cnts['SP'] += d.get('SP', 0)
            tot_cnts['TEP'] += d.get('TEP', 0)
            tot_cnts['WP'] += d.get('WP', 0)
            tot_cnts['TWP'] += d.get('TWP', 0)
            tot_cnts['NTS'] += d.get('NTS', 0)
            tot_cnts['OTHERS'] += d.get('OTHERS', 0)
        try:
            if order_key is not None:
                orders_list = self.filt_orders(orders_list, order_key)
        except: pass
        datas = {'orders_list': orders_list, 'tot_cnts': tot_cnts,
                 'current_url': current_url, 'keyword': keyword}
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Order List')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteCreateOrderView(View):
    def filt_refid(self, ref_id):
        ref_id = str(ref_id)[::-1]
        r = ''
        for i in ref_id:
            if i.isdigit():
                r += i
            else:
                break
        if r:
            return int(r[::-1])
        return 0

    def after_delete_trackid(self, createorder_model, comp_obj, ref_id):
        ref_id = self.filt_refid(ref_id)
        compid = comp_obj.id
        if isinstance(comp_obj.create_orderid_track, dict):
            bref_id = comp_obj.create_orderid_track.get(str(compid), ref_id)
            bref_id = self.filt_refid(bref_id)
            if bref_id < ref_id:
                comp_obj.create_orderid_track = {compid: f'{comp_obj.company_id}{ref_id}'}
                comp_obj.save()
            else:
                comp_obj.create_orderid_track=  {compid: f'{comp_obj.company_id}{bref_id}'}
                comp_obj.save()
        else:
            comp_obj.create_orderid_track = {compid: f'{comp_obj.company_id}{ref_id}'}
            comp_obj.save()

    def get(self, request, id, pass_type):
        try:
            order = models.CreateOrderModel.objects.get(id=id)
            comp = order.company.company_name
            comp_id = order.company.id
            compmodel = models.AddCompanyModel.objects.get(id=comp_id)
            ref_id = order.ref_id

            order.delete()
            self.after_delete_trackid(
                    models.CreateOrderModel.objects.filter(company=compmodel),
                    compmodel, ref_id)

            messages.success(request, f'{comp} Deleted.')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {comp} Order')
        except Exception as e:
            messages.error(request, f'Error: {e}')

        return redirect(f'/client-management/order-list/{comp_id}?keyword={pass_type}')

@method_decorator(login_required(login_url="/"), name='dispatch')
class UpdateOrderView(View):
    def post(self, request, id):
        application_id = request.POST.get('application-id')
        result = request.POST.get('result')
        try:
            order = models.CreateOrderModel.objects.get(id=id)
            order.application_id = application_id
            order.result = result
            order.save()
            messages.success(request, f'{order.company.company_name} Updated..')
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return redirect('/client-management/order-list')

# -------------------------------------------------------------------------------


def create_buying_selling_api(request, id=None, return_url=None):
    if request.method == 'POST':
        submit_date = request.POST.get('date')
        business_type = request.POST.get('business-type')
        rental_deposite = request.POST.get('rental-deposite')
        staff_needed = request.POST.get('staff-needed')
        take_over_fee = request.POST.get('take-over-fee')
        remarks = request.POST.get('remarks')
        status = request.POST.get('status')
        employeer = request.POST.get('employeer')
        address = request.POST.get('address')
        sales_details = request.POST.get('sales-details')
        company_details = request.POST.get('company-details')
        recommended_buyers = request.POST.get('recommended-buyers')
        upload_docs = request.FILES.getlist('file[]')
        upload_video = request.FILES.get('video')
        try:
            staff_needed = int(staff_needed)
        except:
            staff_needed = None
        try:
            submit_date = datetime.strptime(submit_date, '%d/%m/%Y')
        except:
            submit_date = None
        if id:
            try:
                employeer = models.NewClientModel.objects.get(id=employeer)
                edit_buy_sell = models.BuyingSellingModel.objects.get(id=id)
                edit_buy_sell.submit_date=submit_date
                edit_buy_sell.business_type=business_type
                edit_buy_sell.rental_deposite=rental_deposite
                edit_buy_sell.staff_needed=staff_needed
                edit_buy_sell.take_over_fee=take_over_fee
                edit_buy_sell.remarks=remarks
                edit_buy_sell.employeer=employeer
                edit_buy_sell.address=address
                edit_buy_sell.sales_details=sales_details
                edit_buy_sell.company_details=company_details
                edit_buy_sell.recommended_buyers=recommended_buyers
                edit_buy_sell.status=status
                if upload_video:
                    edit_buy_sell.video = upload_video
                edit_buy_sell.save()
                if upload_docs:
                    edit_buy_sell.attachments.clear()
                    for doc in upload_docs:
                        attach = models.BuyingSellingAttachmentsModel(attachments=doc)
                        attach.save()
                        edit_buy_sell.attachments.add(attach)
                return_url = url_encode_func(return_url, encode=False)
                messages.success(request, f'Employeer : {employeer.client_name} Updated..')
                response_data = {'status': 'success', 'msg': f'Employeer : {employeer.client_name} Updated..',
                                    'return_url': str(return_url)}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'success', 'msg': str(e),
                                    'return_url': '/client-management/buying-selling-form'}
            return JsonResponse(response_data)
        else:
            try:
                employeer = models.NewClientModel.objects.get(id=employeer)
                create_buy_sell = models.BuyingSellingModel(submit_date=submit_date, business_type=business_type,
                        rental_deposite=rental_deposite, staff_needed=staff_needed, take_over_fee=take_over_fee,
                        remarks=remarks, status=status, employeer=employeer, address=address, sales_details=sales_details,
                        company_details=company_details, recommended_buyers=recommended_buyers, video=upload_video)
                create_buy_sell.save()

                for doc in upload_docs:
                    attach = models.BuyingSellingAttachmentsModel(attachments=doc)
                    attach.save()
                    create_buy_sell.attachments.add(attach)
                messages.success(request, 'New Buying & Selling Created..')
                response_data = {'status': 'success', 'msg': 'New Buying & Selling Created..'}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e)}
            return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class BuyingSellingFormView(View):
    template_name = 'buying-selling-form.html'
    def get(self, request, id=None, return_url=None):
        employeers = models.NewClientModel.objects.all()
        datas = {
            'employeers': employeers,
        }
        if id:
            try:
                edit_buy_sell=models.BuyingSellingModel.objects.get(id=id)
                datas['edit_buy_sell']=edit_buy_sell
                datas['return_url']=return_url
                datas['edit_buy_sell_date']=edit_buy_sell.submit_date.strftime('%d/%m/%Y')
            except:
                pass
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed BuyingSelling Form Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class BuyingSellingListView(View):
    template_name='buying-selling-list.html'
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
            buying_selling = models.BuyingSellingModel.objects.filter(Q(employeer__client_name__icontains=keyword)|
                        Q(business_type__icontains=keyword)|Q(address__icontains=keyword)|Q(staff_needed__icontains=keyword)|
                        Q(rental_deposite__icontains=keyword)|Q(sales_details__icontains=keyword)|Q(status__icontains=keyword)|
                        Q(company_details__icontains=keyword)|Q(take_over_fee__icontains=keyword)|Q(recommended_buyers__icontains=keyword)|
                        Q(remarks__icontains=keyword))
        else:
            buying_selling = models.BuyingSellingModel.objects.all()
        buying_selling_page = Paginator(buying_selling, 25)
        page_number = request.GET.get('page')
        buyers_contact = models.BuyerFormModel.objects.all()
        try:
            buying_selling_page = buying_selling_page.get_page(page_number)
        except PageNotAnInteger:
            buying_selling_page = buying_selling_page.page(1)
        except EmptyPage:
            buying_selling_page = buying_selling_page.page(buying_selling_page.num_pages)
        datas = {
            'buying_selling': buying_selling_page,
            'current_url': current_url,
            'keyword': keyword,
            'result_cnt': buying_selling.count(),
            'return_url': url_encode_func(request.get_full_path()),
            'buyers_contact': buyers_contact,
        }
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed BuyingSelling List Page')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteBuyingSellingView(View):
    def get(self, request, id, return_url):
        try:
            app_queue = models.BuyingSellingModel.objects.get(id=id)
            app_queue.delete()
            messages.success(request, f'BuySell ID : {id} Deleted..')
            try:
                return redirect(url_encode_func(return_url, encode=False))
            except Exception:
                return redirect('/client-management/buying-selling-list')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted ID:{id} BuyingSelling')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('/client-management/buying-selling-list')

def whatsapp_message(data):
    # `*Date:* ${ord_date}%0a*RefID:* ${ord_ref_id}%0a*Description:* ${ord_desc}%0a*PassType:* ${ord_pass_type}%0a`
    datas = {
            'BusinessType': data.business_type,
            'RentalDeposite': data.rental_deposite,
        }
    if data.video:
        datas['Video'] = f'https://myindiaoverseas.pythonanywhere.com{data.video.url}'
    if data.attachments.all():
        datas['Images'] = ', '.join([f'https://myindiaoverseas.pythonanywhere.com{i.attachments.url}'
                                    for i in data.attachments.all()])
    cols = [ f'*{k}:* ' for k in datas.keys() ]
    vals = [ f'{v}%0a' for v in datas.values() ]
    message = ''.join([f'{i[0]}{i[1]}' for i in zip(cols, vals)])
    return message

class BuyerInfoWhatsapp(View):
    def post(self, request, id):
        buyer_id = request.POST.get('buyer')
        remarks = request.POST.get('remarks')
        buyer = models.BuyerFormModel.objects.get(id=buyer_id)
        seller = models.BuyingSellingModel.objects.get(id=id)
        phone = buyer.whatsapp_number
        datas = whatsapp_message(seller)
        if remarks:
            datas = f'{datas}%0a{remarks}'
        response_data = {'status': 'success',
                         'phone': f'{phone}',
                         'seller_data': datas}
        return JsonResponse(response_data)

class SellerInfoWhatsapp(View):
    def get(self, request, id):
        seller = models.BuyingSellingModel.objects.get(id=id)
        return JsonResponse({'status': 'success', 'seller': seller.employeer.client_name})

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreatePaySlipAPIView(View):
    def post(self, request, tep_id, id=None, return_url=None):
        payslip_from = request.POST.get('payslip-from')
        payslip_to = request.POST.get('payslip-to')
        basic_pay = request.POST.get('basic-pay')
        basic_pay = basic_pay if basic_pay else 0
        advance = request.POST.get('advance')
        advance = advance if advance else 0
        date_of_payment = request.POST.get('date-of-payment')
        overtime_payment = request.POST.get('overtime-payment')
        overtime_payment = overtime_payment if overtime_payment else 0
        other_additional = request.POST.get('other-additional')
        other_additional = other_additional if other_additional else 0
        total_allowance = request.POST.get('total-allowance')
        total_allowance = total_allowance if total_allowance else 0
        emp_cpf_deduction = request.POST.get('emp-cpf-deduction')
        emp_cpf_deduction = emp_cpf_deduction if emp_cpf_deduction else 0
        mode_of_payment = request.POST.get('mode-of-payment')
        overtime_hours = request.POST.get('overtime-hours')
        overtime_hours = overtime_hours if overtime_hours else 0
        emp_cpf_contribution = request.POST.get('emp-cpf-contribution')
        emp_cpf_contribution = emp_cpf_contribution if emp_cpf_contribution else 0

        try:
            payslip_from = datetime.strptime(payslip_from, '%Y-%m-%d')
        except:
            payslip_from = None
        try:
            payslip_to = datetime.strptime(payslip_to, '%Y-%m-%d')
        except:
            payslip_to = None
        try:
            date_of_payment = datetime.strptime(date_of_payment, '%Y-%m-%d')
        except:
            date_of_payment = None

        if id:
            try:
                net_pay = int(basic_pay) + int(total_allowance) + int(overtime_payment) + int(overtime_hours) + int(other_additional)
                total_deduction = int(advance) + int(emp_cpf_deduction)
                net_pay = net_pay - total_deduction
                after_approved_tep = AfterApprovalTEPModel.objects.get(id=tep_id)
                update_payslip = models.PaySlipModel.objects.get(id=id)
                update_payslip.payslip_date_from=payslip_from
                update_payslip.payslip_date_to=payslip_to
                update_payslip.after_approved_tep=after_approved_tep
                update_payslip.basic_pay=basic_pay
                update_payslip.advance=advance
                update_payslip.payment_date=date_of_payment
                update_payslip.overtime_payment_period=overtime_payment
                update_payslip.other_additional=other_additional
                update_payslip.total_allowance=total_allowance
                update_payslip.net_pay=net_pay
                update_payslip.employee_cpf_deduction=emp_cpf_deduction
                update_payslip.mode_of_payment=mode_of_payment
                update_payslip.overtime_work_hours=overtime_hours
                update_payslip.employee_cpf_contribution=emp_cpf_contribution
                update_payslip.total_deduction=total_deduction
                update_payslip.save()
                return_url = url_encode_func(return_url, encode=False)
                messages.success(request, f'{after_approved_tep.workpass.name} - Payslip Updated..')
                response_data = {'status': 'success', 'msg': 'Payslip Updated..', 'return_url': str(return_url)}
            except Exception as e:
                return_url = url_encode_func(return_url, encode=False)
                response_data = {'status': 'error', 'msg': str(e), 'return_url': str(return_url)}
        else:
            try:
                net_pay = int(basic_pay) + int(total_allowance) + int(overtime_payment) + int(overtime_hours) + int(other_additional)
                total_deduction = int(advance) + int(emp_cpf_deduction)
                net_pay = net_pay - total_deduction
                after_approved_tep = AfterApprovalTEPModel.objects.get(id=tep_id)
                create_payslip = models.PaySlipModel(after_approved_tep=after_approved_tep, payslip_date_from=payslip_from,
                                payslip_date_to=payslip_to, basic_pay=basic_pay, advance=advance,
                                payment_date=date_of_payment, overtime_payment_period=overtime_payment,
                                other_additional=other_additional, total_allowance=total_allowance, net_pay=net_pay,
                                employee_cpf_deduction=emp_cpf_deduction, mode_of_payment=mode_of_payment,
                                overtime_work_hours=overtime_hours, employee_cpf_contribution=emp_cpf_contribution,
                                total_deduction=total_deduction)
                create_payslip.save()
                messages.success(request, f'{after_approved_tep.workpass.name} - New Payslip Created..')
                response_data = {'status': 'success', 'msg': 'New Payslip Created..'}
            except Exception as e:
                messages.error(request, f'{e}')
                response_data = {'status': 'error', 'msg': str(e)}
        print(response_data)
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class PaySlipListView(View):
    template_name = 'payslip-list.html'
    def get(self, request, tep_id):
        after_tep = AfterApprovalTEPModel.objects.get(id=tep_id)
        payslips = models.PaySlipModel.objects.filter(after_approved_tep=tep_id)
        datas = {
            'current_date': datetime.today().date,
            'payslips': payslips,
            'after_tep': after_tep,
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ApprovedEmpPayslipView(View):
    template_name = 'approved-emp-payslip.html'
    def get(self, request, id):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()

        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        try:
            company=models.AddCompanyModel.objects.get(id=id)
        except:
            return redirect('/client-management/grouped-companies-payslip')

        if keyword:
            after_approved_tep = AfterApprovalTEPModel.objects.filter(
                Q(workpass__company_name__company_name__icontains=keyword)|
                Q(workpass__name__icontains=keyword)|
                Q(workpass__fin_number__icontains=keyword)|
                Q(workpass__company_name__company_id__icontains=keyword)
            ).filter(issue__isnull=False, workpass__company_name__isnull=False, workpass__company_name=company)
        else:
            after_approved_tep = AfterApprovalTEPModel.objects.filter(issue__isnull=False,
                                    workpass__company_name__isnull=False, workpass__company_name=company)

        after_approved_tep_page = Paginator(after_approved_tep.order_by(
            'workpass__company_name__client__client_id', 'workpass__company_name__company_id'), 25)
        page_number = request.GET.get('page')

        try:
            after_approved_tep_page = after_approved_tep_page.get_page(page_number)
        except PageNotAnInteger:
            after_approved_tep_page = after_approved_tep_page.page(1)
        except EmptyPage:
            after_approved_tep_page = after_approved_tep_page.page(after_approved_tep_page.num_pages)
        datas = {
            'current_date': datetime.today().date,
            'after_approved': after_approved_tep_page,
            'current_url': current_url,
            'result_cnt': after_approved_tep.count(),
            'keyword': keyword,
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class GeneratePaySlipView(View):
    template_name = 'generate-payslip.html'
    def get(self, request, id):
        try:
            payslip = models.PaySlipModel.objects.get(id=id)
            earnings, deductions = [], []
            if payslip.basic_pay:
                earnings.append('A')
            if payslip.total_allowance:
                earnings.append('B')
            if payslip.overtime_payment_period:
                earnings.append('C')
            if payslip.overtime_work_hours:
                earnings.append('D')
            if payslip.other_additional:
                earnings.append('E')
            if payslip.advance:
                deductions.append('F')
            if payslip.employee_cpf_deduction:
                deductions.append('G')

            earnings, deductions = '+'.join(earnings), '+'.join(deductions)
            earn_deduct = f'({earnings})'
            if deductions:
                earn_deduct = earn_deduct + f' - ({deductions})'

            datas = {'payslip': payslip, 'earn_deduct': earn_deduct}
        except:
            datas = {}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class UpdatePaySlipView(View):
    template_name="edit-payslip.html"
    def get(self, request, tep_id, id, return_url):
        after_tep = AfterApprovalTEPModel.objects.get(id=tep_id)
        payslip = models.PaySlipModel.objects.get(id=id)
        payment_mode = ['Cash', 'Cheque', 'Bank Deposit']
        datas = {
            'payslip': payslip, 'payment_mode': payment_mode,
            'return_url': return_url,
            'after_tep': after_tep,
        }
        try:
            datas['payslip_date_from'] = payslip.payslip_date_from.strftime('%Y-%m-%d')
            datas['payslip_date_to'] = payslip.payslip_date_to.strftime('%Y-%m-%d')
            datas['payment_date'] = payslip.payment_date.strftime('%Y-%m-%d')
        except: pass
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class PrintPayslipView(View):
    template_name = 'print-payslip.html'
    def get(self, request, id):
        payslip = models.PaySlipModel.objects.get(id=id)
        datas = {'payslip': payslip}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class GroupedCompaniesPaySlipView(View):
    template_name='grouped-comp-payslip.html'
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
            after_approved = AfterApprovalTEPModel.objects.filter(
                Q(workpass__company_name__company_name__icontains=keyword)|
                Q(workpass__company_name__company_id__icontains=keyword)
            ).filter(issue__isnull=False, workpass__company_name__isnull=False).order_by(
            'workpass__company_name__client__client_id', 'workpass__company_name__company_id').values(
            'workpass__company_name__id', 'workpass__company_name__company_id',
            'workpass__company_name__company_name').annotate(count=Count('workpass__company_name'))
        else:
            after_approved = AfterApprovalTEPModel.objects.filter(issue__isnull=False,
                workpass__company_name__isnull=False).order_by('workpass__company_name__client__client_id',
                'workpass__company_name__company_id').values('workpass__company_name__id',
                'workpass__company_name__company_id',
                'workpass__company_name__company_name').annotate(count=Count('workpass__company_name'))

        after_approved_tep_page = Paginator(after_approved, 25)
        page_number = request.GET.get('page')

        try:
            after_approved_tep_page = after_approved_tep_page.get_page(page_number)
        except PageNotAnInteger:
            after_approved_tep_page = after_approved_tep_page.page(1)
        except EmptyPage:
            after_approved_tep_page = after_approved_tep_page.page(after_approved_tep_page.num_pages)
        datas = {
            'current_date': datetime.today().date,
            'after_approved': after_approved_tep_page,
            'current_url': current_url,
            'result_cnt': after_approved.count(),
            'keyword': keyword,
            'return_url': url_encode_func(request.get_full_path()),
        }
        return render(request, self.template_name, context=datas)

def column_check_func(ws):
    status = True
    if 'CompanyID' !=  ws.cell(row=1, column=1).value:
        status = False
    if 'Name' !=  ws.cell(row=1, column=2).value:
        status = False
    if 'NRIC/FIN' !=  ws.cell(row=1, column=3).value:
        status = False
    if 'Pass' !=  ws.cell(row=1, column=4).value:
        status = False
    if 'JobTitle' !=  ws.cell(row=1, column=5).value:
        status = False
    if 'IssueDate(dd/mm/yyyy)' !=  ws.cell(row=1, column=6).value:
        status = False
    if 'CancelDate(dd/mm/yyyy)' !=  ws.cell(row=1, column=7).value:
        status = False
    if 'FixedMonthlySalary' !=  ws.cell(row=1, column=8).value:
        status = False
    if 'BasicMontlySalary' !=  ws.cell(row=1, column=9).value:
        status = False
    if 'Allowance' !=  ws.cell(row=1, column=10).value:
        status = False
    return status

def find_max_row_and_empty_cells(ws):
    EmptyRow = []
    for row in range(2, ws.max_row+1):
        col1 = ws.cell(row=row, column=1)
        col2 = ws.cell(row=row, column=2)
        col3 = ws.cell(row=row, column=3)
        col6 = ws.cell(row=row, column=6)
        col7 = ws.cell(row=row, column=7)
        col8 = ws.cell(row=row, column=8)
        col9 = ws.cell(row=row, column=9)
        col10 = ws.cell(row=row, column=10)

        if col1.value is None:
            EmptyRow.append(f'{col1.coordinate} Cell is Empty. It"s mandatory Field.')
        if col2.value is None:
            EmptyRow.append(f'{col2.coordinate} Cell is Empty. It"s mandatory Field.')
        if col3.value is None:
            EmptyRow.append(f'{col3.coordinate} Cell is Empty. It"s mandatory Field.')
        if col6.value is None:
            EmptyRow.append(f'{col6.coordinate} Cell is Empty. It"s mandatory Field.')
        if col7.value is None:
            EmptyRow.append(f'{col7.coordinate} Cell is Empty. It"s mandatory Field.')
        if col8.value is None:
            EmptyRow.append(f'{col8.coordinate} Cell is Empty. It"s mandatory Field.')
        if col9.value is None:
            EmptyRow.append(f'{col9.coordinate} Cell is Empty. It"s mandatory Field.')
        if col10.value is None:
            EmptyRow.append(f'{col10.coordinate} Cell is Empty. It"s mandatory Field.')

        if (col1.value is None and col2.value is None and col3.value is None and col6.value is None
                    and col7.value is None and col8.value is None and col9.value is None and col10.value is None):
            return row, EmptyRow
    return row, EmptyRow

@method_decorator(login_required(login_url="/"), name='dispatch')
class NewCandidateExcelUploadAPI(View):
    def post(self, request):
        try:
            myFile = request.FILES.get('myFile')
            if not myFile.name.endswith('.xlsx'):
                response_data = {'status': 'error', 'msg': ['Error: File Format Not Allowed!']}
                return JsonResponse(response_data)
            wb = openpyxl.load_workbook(myFile)
            ws = wb.worksheets[0]
            col_check = column_check_func(ws)
            if not col_check:
                response_data = {'status': 'error', 'msg': ['Error: Please Check Column Names']}
                return JsonResponse(response_data)
            max_row, empty_rows = find_max_row_and_empty_cells(ws)
            if empty_rows:
                response_data = {'status': 'error', 'msg': empty_rows}
                return JsonResponse(response_data)
            companies_errors, bulk_create_datas = [], []
            for row in range(2, max_row+1):
                company_id = str(ws.cell(row=row, column=1).value).strip()
                name = ws.cell(row=row, column=2).value
                nric_fin = ws.cell(row=row, column=3).value
                passtype = ws.cell(row=row, column=4).value
                chk_comp = models.AddCompanyModel.objects.filter(company_id=company_id)
                chk_fin = WorkPassModel.objects.filter(fin_number=nric_fin)
                if not chk_comp:
                    companies_errors.append(f'Not Exist, CompanyId : {company_id}, Row: {ws.cell(row=row, column=1).coordinate}')
                if chk_fin:
                    companies_errors.append(f'Already Exist, NRIC/FIN : {nric_fin}, Row: {ws.cell(row=row, column=3).coordinate}')
                if chk_comp and not chk_fin:
                    bulk_create_datas.append(WorkPassModel(job=None, doa=datetime.today(), fin_number=nric_fin,
                            application_no=f'{datetime.today().strftime("%d%m%y")}{random.randint(100000, 999999)}',
                            name=name, company_name=chk_comp.first(), epass_type=passtype, status='APPROVED'))
            if companies_errors:
                response_data = {'status': 'error', 'msg': companies_errors}
                return JsonResponse(response_data)
            if not companies_errors:
                WorkPassModel.objects.bulk_create(bulk_create_datas)
            messages.success(request, f'{len(bulk_create_datas)} rows inserted..')
            response_data = {'status': 'success', 'msg': ['Done.']}
        except Exception as e:
            messages.error(request, f'Error: {e}')
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AddNewCandidateExcelUpload(View):
    template_name = 'new-candidate-excel-upload.html'
    def get(self, request):
        return render(request, self.template_name)

@method_decorator(login_required(login_url="/"), name='dispatch')
class BuyerFormView(View):
    template_name = 'buyer-form.html'
    def get(self, request, id=None):
        employeers = models.NewClientModel.objects.all()
        datas = {
            'employeers': employeers,
        }
        if id:
            try:
                datas['buyer'] = models.BuyerFormModel.objects.get(id=id)
            except: pass
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Buyer Form Page')
        return render(request, self.template_name, context=datas)
    def post(self, request, id=None):
        employeer = request.POST.get('employeer')
        contact_number = request.POST.get('contact-number')
        whatsapp_number = request.POST.get('whatsapp-number')
        requirement = request.POST.get('requirement')
        try:
            employeer = models.NewClientModel.objects.get(id=employeer)
            if id:
                buyer = models.BuyerFormModel.objects.get(id=id)
                buyer.employeer = employeer
                buyer.contact_number = contact_number
                buyer.whatsapp_number = whatsapp_number
                buyer.requirement = requirement
                buyer.save()
                messages.success(request, f'{employeer.client_name} Updated..')
                return redirect('/client-management/buyer-list')
            else:
                buyer = models.BuyerFormModel(employeer=employeer, contact_number=contact_number,
                                          whatsapp_number=whatsapp_number, requirement=requirement)
                buyer.save()
                messages.success(request, f'New Buyer Added..')
        except Exception as e:
            messages.error(request, f'Error {e}')
        return redirect('/client-management/buyer-form')

@method_decorator(login_required(login_url="/"), name='dispatch')
class BuyerListView(View):
    template_name = 'buyer-list.html'
    def get(self, request):
        buyers = models.BuyerFormModel.objects.all()
        datas = {'buyers': buyers}
        db_logger.info(f'<b style="color:red">{request.user}</b>: Accessed Buyers List')
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteBuyerView(View):
    def get(self, request, id):
        try:
            buyer = models.BuyerFormModel.objects.get(id=id)
            employeer_name = buyer.employeer.client_name
            buyer.delete()
            messages.success(request, f'{employeer_name} Deleted..')
            db_logger.info(f'<b style="color:red">{request.user}</b>: Deleted {employeer_name} Buyer')
        except Exception as e:
            messages.error(request, f'Error {e}')
        return redirect('/client-management/buyer-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class VoiceChangerView(View):
    template_name="voice-changer.html"

    def change_pitch(self, sound, octaves):
        new_sample_rate = int(sound.frame_rate * (0.8 ** octaves))
        return sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(sound.frame_rate)

    def change_speed(self, sound, factor):
        return sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * factor)
        }).set_frame_rate(sound.frame_rate)

    def process_audio(self, audio_bytes, pitch_change, speed_change):
        audio = AudioSegment.from_file(audio_bytes)
        modified_audio = self.change_pitch(audio, pitch_change)
        modified_audio = self.change_speed(modified_audio, speed_change)

        out_bytes = BytesIO()
        modified_audio.export(out_bytes, format="mp3")
        out_bytes.seek(0)
        return out_bytes.getvalue()

    def get(self, request):
        voice_changer = models.VoiceChangerUploadFileModel.objects.all()
        datas = {
            'voice_changer': voice_changer
        }
        return render(request, self.template_name, context=datas)

    def post(self, request):
        voice = request.FILES.get('audio')
        filename = f'{voice}'
        try:
            voice = self.process_audio(voice, 1, 1.6)
            voice = InMemoryUploadedFile(
                        file=BytesIO(voice),
                        field_name=None,
                        name=filename,
                        content_type='audio/mpeg',
                        size=len(voice),
                        charset=None
                    )
            vc = models.VoiceChangerUploadFileModel(audio=voice)
            vc.save()
            messages.success(request, f'Voice Changed..')
            response_data = {'status': 'success'}
        except Exception as e:
            messages.error(request, f'Error: {e}')
            response_data = {'status': 'error'}
        return JsonResponse(response_data)
