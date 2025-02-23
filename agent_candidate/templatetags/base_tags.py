from django import template
from agent_candidate import models
import re, xlsxwriter, inflect, calendar
from hurry.filesize import size
from client_management.models import AddCompanyModel
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from job_advertisement.models import StaffMaintenanceModel
from mom_application.models import AfterApprovalTEPModel

register = template.Library()

@register.filter('has_group')
def has_group(user, group_name):
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False

@register.filter
def norm_id(id):
    cand = models.CandidateFormModels.objects.first()
    if id == 1:
        return id
    else:
        rem = id - cand.id
        if rem == 0:
            return 1
        return (id-cand.id)+1

@register.filter
def check_folder(url):
    chk = re.findall('/agent-candidate/candidate-details/[0-9]+$', url)
    if chk:
        return chk[0]
    return ''

@register.filter
def bytes_to_mb(filesize):
    return size(filesize)

@register.filter
def get_candidate_details(candidate):
    cand = models.AgentFormModel.objects.filter(candidate=candidate)
    if cand:
        c = cand.first()
        dob = c.candidate_dob if c.candidate_dob else '-'
        job = c.job_title if c.job_title else '-'
        edu = c.candidate_high_edu if c.candidate_high_edu else '-'
        return dob, job, edu
    return '-', '-', '-'

@register.filter
def get_folder_name(folder, title):
    # /agent-candidate/candidate-details/
    if title.title == folder.title.title:
        return f"/agent-candidate/candidate-details/{folder.id}"
    return

@register.filter
def mtm_users(task, all=False):
    users = task.asigned_to.all()
    if all:
        return f"{', '.join([usr.user.username for usr in users])}"
    if users:
        if len(users) >= 2:
            return f"{', '.join([usr.user.username for usr in users][:2])}, etc.."
        return f"{', '.join([usr.user.username for usr in users][:2])}"
    return '-'

@register.filter
def no_of_companies(client):
    datas = AddCompanyModel.objects.filter(client=client)
    return datas

@register.filter
def none_handle(data):
    return '-' if data == 'None' or data is None else data

@register.filter
def remaining_days(exp_date):
    today = datetime.today().date()
    try:
        if exp_date >= today:
            t = exp_date - today
            return t.days
        return 0
    except:
        return '-'

@register.filter
def pending_days(app_date):
    today = datetime.today().date()
    try:
        p = today - app_date
        if p.days > 0:
            return p.days
        return 0
    except:
        return '-'

@register.filter
def get_invoice_data(data):
    try:
        header = '\n'.join([f'<th style="text-align:center">{col}</th>' for col in data[0]])
        body_data = data[:]
        table_rows='\n'.join(['<tr>'+'\n'.join([f'<td style="text-align:center">{col[j]}</td>'
                                    for j in col])+'</tr>' for col in body_data])
        html = f'''
                <thead>
                    <tr>
                    {header}
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
                '''
        return html
    except:
        return ''

@register.filter
def null_handle(data):
    if data:
        return data
    return '-'

@register.filter
def future_due_tep(data):
    try:
        data = data + timedelta(days=90)
        t = datetime.today().date()
        t = data - t
        return t.days
    except:
        return '-'

@register.filter
def forcounter_serialno(serial_num, page_num):
    try:
        if page_num.number == 1:
            return serial_num
        return serial_num + ((page_num.number-1)*25)
    except:
        return serial_num

@register.filter
def gmail_date_fix(gmail_date):
    try:
        return gmail_date + timedelta(hours=5, minutes=30)
    except:
        return gmail_date

@register.filter
def column_num_to_name(agent_id):
    try:
        return f"{xlsxwriter.utility.xl_col_to_name(agent_id)}"
    except:
        return '-'

@register.filter
def get_filename(filename):
    try:
        return filename.split('/')[-1]
    except:
        return filename

@register.filter
def slice_filename(filename):
    try:
        return f'{filename[:10]}..'
    except:
        return filename

@register.filter
def amount_to_words(amt):
    try:
        if amt:
            p = inflect.engine()
            return f'({p.number_to_words(amt).replace(",", "").title()})'
    except:
        return

@register.filter
def data_padding(data):
    try:
        if len(str(data)) > 16:
            return str(data)[:16] + '..'
        return data
    except:
        return data

@register.filter
def get_company(datas, tot_cnts):
    try:
        result = '''
                <thead>
                    <tr>
                        <th style="text-align:center">CompanyID</th>
                        <th style="text-align:center">CompanyName</th>
                        <th style="text-align:center">ROC</th>
                        <th style="text-align:center">EP:<a href="/client-management/grouped-order-list/EP">{}</a></th>
                        <th style="text-align:center">SP:<a href="/client-management/grouped-order-list/SP">{}</a></th>
                        <th style="text-align:center">TEP:<a href="/client-management/grouped-order-list/TEP">{}</a></th>
                        <th style="text-align:center">WP:<a href="/client-management/grouped-order-list/WP">{}</a></th>
                        <th style="text-align:center">TWP:<a href="/client-management/grouped-order-list/TWP">{}</a></th>
                        <th style="text-align:center">NTS:<a href="/client-management/grouped-order-list/NTS">{}</a></th>
                        <th style="text-align:center">OTHERS:<a href="/client-management/grouped-order-list/OTHERS">{}</a></th>
                    </tr>
                </thead>
                <tbody>
                {}
                </tbody>
                 '''
        trow = []
        for compid in datas:
            comp = AddCompanyModel.objects.get(id=compid)
            r = [
                f'<td style="text-align:center">{comp.company_id}</td>',
                f'<td style="text-align:center">{comp.company_name}</td>',
                f'<td style="text-align:center">{comp.roc}</td>']
            d = datas[compid]
            for i in d:
                tag = f'''<td style="text-align:center">
                            <a href="/client-management/order-list/{compid}?keyword={i}">{d[i]}</a>
                        </td>
                    '''
                r.append(tag)
            trow.append('<tr>{}</tr>'.format("\n".join(r)))
        t = (tot_cnts.get('EP', 0), tot_cnts.get('SP', 0), tot_cnts.get('TEP', 0), tot_cnts.get('WP', 0),
            tot_cnts.get('TWP', 0), tot_cnts.get('NTS', 0), tot_cnts.get('OTHERS', 0))
        return result.format(*t, '\n'.join(trow))
    except:
        return ['-', '-', '-'] + (['-']*5)

@register.filter
def convert_utc_ind_time(data):
    try:
        return data + timedelta(hours=5, minutes=30)
    except:
        return data

@register.filter
def cpf_tracker_data_exist(comp, col):
    try:
        if not comp.cpf_tracker:
            return ''
        return comp.cpf_tracker.monthly_update.get(f'{comp.id}_{col}', '')
    except Exception as e:
        return ''

@register.filter
def cpf_tracker_hr_exist(comp, col):
    try:
        if not comp.cpf_tracker:
            return ''
        return comp.cpf_tracker.hr_info.get(f'{comp.id}_{col}', '')
    except Exception as e:
        return ''

def need_col_parse(comp):
    '''
        Formula: NEED=(SP+WP+NTS+PRC+TWP)*2
    '''
    try:
        sp = comp.cpf_tracker.monthly_update.get(f'{comp.id}_sp', 0)
        sp = eval(str(sp).strip())
        if not isinstance(sp, (float, int)):
            sp = 0
    except:
        sp = 0
    try:
        wp = comp.cpf_tracker.monthly_update.get(f'{comp.id}_wp', 0)
        wp = eval(str(wp).strip())
        if not isinstance(wp, (float, int)):
            wp = 0
    except:
        wp = 0
    try:
        nts = comp.cpf_tracker.monthly_update.get(f'{comp.id}_nts', 0)
        nts = eval(str(nts).strip())
        if not isinstance(nts, (float, int)):
            nts = 0
    except:
        nts = 0
    try:
        prc = comp.cpf_tracker.monthly_update.get(f'{comp.id}_prc', 0)
        prc = eval(str(prc).strip())
        if not isinstance(prc, (float, int)):
            prc = 0
    except:
        prc = 0
    try:
        twp = comp.cpf_tracker.monthly_update.get(f'{comp.id}_twp', 0)
        twp = eval(str(twp).strip())
        if not isinstance(twp, (float, int)):
            twp = 0
    except:
        twp = 0

    return (sp+wp+nts+prc+twp)*2

def get_previous_six_months():
    import calendar
    months = {1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL', 5: 'MAY', 6: 'JUNE',
    7: 'JULY', 8: 'AUGUST', 9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'}
    previous_6_months = []
    current_date = datetime.today()
    for _ in range(1, 7):
        prev_month = calendar._prevmonth(current_date.year, current_date.month)
        current_date = datetime(year=prev_month[0], month=prev_month[1], day=1)
        colname = f"{months[prev_month[1]][:3]}{prev_month[0]}"
        previous_6_months.append(colname)

    return previous_6_months[::-1]

def available_col_parse(comp):
        '''
            Formula: AVAIL=[FULL+(PART/2)]+[FULL+(PART/2)]+[FULL+(PART/2)]/3
        '''
        prev_3_months = get_previous_six_months()[-4:-1]
        avail = 0
        div_cnt = 0
        for mon in prev_3_months:
            try:
                fulltime = comp.cpf_tracker.monthly_update.get(f'{comp.id}_{mon}_full', 0)
                fulltime = eval(str(fulltime).strip())
                if not isinstance(fulltime, (float, int)):
                    fulltime = 0
            except:
                fulltime = 0
            try:
                parttime = comp.cpf_tracker.monthly_update.get(f'{comp.id}_{mon}_part', 0)
                parttime = eval(str(parttime).strip())
                if not isinstance(parttime, (float, int)):
                    parttime = 0
            except:
                parttime = 0
            if parttime != 0 or fulltime != 0:
                div_cnt += 1
            avail = avail + (fulltime + (parttime/2))
        if div_cnt == 0:
            return 0
        return eval(f'{avail/div_cnt:.1f}')

@register.filter
def local_count_calculator(comp, col):
    try:
        need_col = need_col_parse(comp)
        avail_col = available_col_parse(comp)
        if need_col == 0 and avail_col == 0:
            status_col = ''
        elif need_col > avail_col:
            status_col = 'Check'
        else:
            status_col = 'Clear'
        if col == 'need':
            return need_col
        if col == 'avail':
            return avail_col
        if col == 'status':
            return status_col
        return ''
    except:
        return ''

class FinanaceFormulas:
    def __init__(self):
        self.months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

    def year_end(self, sdate):
        try:
            dd = sdate[:2]
            if dd.isdigit():
                dd = int(dd)
            else:
                dd = int(dd[0])
        except:
            dd = None

        try:
            mm = sdate[-3:].upper()
            mm = self.months[mm]
        except:
            mm = None

        return dd, mm

    def dateParsing(self, sdate):
        dd, mm = self.year_end(sdate)
        if all([dd, mm]):
            curr_year = date.today().year
            fdate = date(year=curr_year, month=mm, day=dd)
            agmstart = fdate + timedelta(days=1)
            agmend = (fdate + relativedelta(months=4))
            agmend_monthend = calendar.monthrange(year=agmend.year, month=agmend.month)
            agmend = date(year=agmend.year, month=agmend.month, day=agmend_monthend[1])

            arstart = agmend + timedelta(days=1)
            arend = (arstart + relativedelta(months=3)) - timedelta(days=1)

            aisstart = date(year=curr_year, month=1, day=1)
            aisend = (aisstart + relativedelta(months=2))

            fyrstart = date(year=curr_year, month=1, day=1)
            fyrend = (fyrstart + relativedelta(months=11)) - timedelta(days=1)

            return agmstart, agmend, arstart, arend, aisstart, aisend, fyrstart, fyrend

@register.simple_tag
def finance_agmend(comp):
    try:
        fin = FinanaceFormulas()
        r = fin.dateParsing(comp.company_review.finance_year_end)
        if r is not None:
            return r
        return ('',) * 8
    except Exception as e:
        return ('',) * 8

@register.filter
def ishrtrackeditable(comp, col):
    try:
        if not comp.cpf_tracker:
            return True
        r = comp.cpf_tracker.hr_info.get(f'{comp.id}_{col}_markasdone', '')
        if r:
            return False
        return True
    except:
        return True

@register.filter
def staff_maintenance_templatetag(user, col):
    try:
        staff = StaffMaintenanceModel.objects.get(user=user)
        key = f'{user.username}-{col}'
        return staff.details.get(key, '')
    except:
        return ''

@register.filter
def get_after_approval_url_tag(wp):
    try:
        a = AfterApprovalTEPModel.objects.filter(workpass=wp)
        if a:
            ipa = a.first()
            ipa = ipa.upload_ipa.url
        else:
            ipa = None
    except:
        ipa = None
    return ipa
