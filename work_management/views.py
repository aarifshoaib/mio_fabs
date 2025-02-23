from django.shortcuts import render, redirect
from django.views import View
from agent_candidate.models import CreateUserModel
from work_management import models
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from client_management.models import NewClientModel, AddCompanyModel, CPFTrackerCompanyModel, CompanyReviewModel
from twilio.rest import Client
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

@method_decorator(login_required(login_url="/"), name='dispatch')
class TasksListView(View):
    template_name = 'tasks-list.html'

    def get(self, request, task_filter=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        if task_filter is None or task_filter == 'Open':
            if keyword:
                try:
                    all_task = models.CreateTaskModel.objects.filter(Q(status='Open')|Q(status__isnull=True)
                            ).filter(Q(subject__subject__icontains=keyword)|Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    all_task = models.CreateTaskModel.objects.filter(Q(status='Open')|Q(status__isnull=True)).order_by('-id')
            else:
                all_task = models.CreateTaskModel.objects.filter(Q(status='Open')|Q(status__isnull=True)).order_by('-id')
            title = 'Open'
        elif task_filter == 'In-Progress':
            if keyword:
                try:
                    all_task = models.CreateTaskModel.objects.filter(status='In-Progress'
                            ).filter(Q(subject__subject__icontains=keyword)|Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    all_task = models.CreateTaskModel.objects.filter(status='In-Progress').order_by('-id')
            else:
                all_task = models.CreateTaskModel.objects.filter(status='In-Progress').order_by('-id')
            title = 'In-Progress'
        elif task_filter == 'Closed':
            if keyword:
                try:
                    all_task = models.CreateTaskModel.objects.filter(status='Closed'
                            ).filter(Q(subject__subject__icontains=keyword)|Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    all_task = models.CreateTaskModel.objects.filter(status='Closed').order_by('-id')
            else:
                all_task = models.CreateTaskModel.objects.filter(status='Closed').order_by('-id')
            title = 'Closed'
        else:
            all_task = models.CreateTaskModel.objects.all().order_by('-id')
            title = 'Open/In-Progress Task'
        users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin', 'HR'])
        get_url = request.get_full_path()

        if 'params' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        # all_task = Paginator(all_task, 15)
        # page_number = request.GET.get('page')

        # try:
        #     all_task = all_task.get_page(page_number)
        # except PageNotAnInteger:
        #     all_task = all_task.page(1)
        # except EmptyPage:
        #     all_task = all_task.page(all_task.num_pages)

        datas = {
            'tasks_list': all_task,
            'users': users,
            'task_title_lists': ['Open', 'In-Progress', 'Closed'],
            'current_url': current_url,
            'title': title,
            'result_cnt': all_task.count(),
            'keyword': keyword,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class ReAssignTaskView(View):
    def get(self, request, id, view_name):
        name = request.GET.get('name')
        try:
            asigned_to = CreateUserModel.objects.get(user__username=name)
            asigned_by = User.objects.get(username=request.user.username)

            task = models.CreateTaskModel.objects.get(id=id)
            task.asigned_by = asigned_by
            task.asigned_to.remove(CreateUserModel.objects.get(user__username=request.user.username))
            task.asigned_to.add(asigned_to)
            task.save()
            messages.success(request, f'Task Assigned To- {asigned_to.user.username}')
        except Exception as e:
            messages.success(request, f'Error: {e}')

        if view_name == 'your-tasks':
            return redirect('/work-management/your-tasks')
        if view_name == 'assigned-tasks':
            return redirect('/work-management/assigned-tasks')
        return redirect('/work-management/tasks-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class YoursTaskView(View):
    template_name = 'your-tasks.html'

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
                your_tasks = models.CreateTaskModel.objects.filter(asigned_to__user__username=request.user.username
                        ).filter(Q(subject__subject__icontains=keyword)|Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
            except:
                your_tasks = models.CreateTaskModel.objects.filter(asigned_to__user__username=request.user.username
                        ).order_by('-id')
        else:
            your_tasks = models.CreateTaskModel.objects.filter(asigned_to__user__username=request.user.username
                        ).order_by('-id')

        users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin'])

        datas = {
            'your_tasks': your_tasks,
            'users': users,
            'result_cnt': your_tasks.count(),
            'keyword': keyword,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AssignedTaskView(View):
    template_name = 'assigned-task.html'

    def get(self, request, task_filter=None):
        keyword = request.GET.get('keyword')
        get_url = request.get_full_path()
        if '?keyword' in get_url:
            get_url = get_url.split('&page=')[0]
            current_url = f"{get_url}&"
        else:
            get_url = get_url.split('?')[0]
            current_url = f"{get_url}?"

        assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username)
        users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin'])

        if task_filter is None or task_filter == 'Open':
            if keyword:
                try:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                    ).filter(Q(status='Open')|Q(status__isnull=True)).filter(Q(subject__subject__icontains=keyword)|
                                     Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(Q(status='Open')|Q(status__isnull=True)).order_by('-id')
            else:
                assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                    ).filter(Q(status='Open')|Q(status__isnull=True)).order_by('-id')
            title = 'Open'
        elif task_filter == 'In-Progress':
            if keyword:
                try:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(status='In-Progress').filter(Q(subject__subject__icontains=keyword)|
                                     Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(status='In-Progress').order_by('-id')
            else:
                assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(status='In-Progress').order_by('-id')
            title = 'In-Progress'
        elif task_filter == 'Closed':
            if keyword:
                try:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(status='Closed').filter(Q(subject__subject__icontains=keyword)|
                                     Q(employer_name__client_name__icontains=keyword)|
                                     Q(company_name__company_name__icontains=keyword)|
                                     Q(asigned_by__username__icontains=keyword)|
                                     Q(asigned_to__user__username__icontains=keyword)).order_by('-id')
                except:
                    assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                        ).filter(status='Closed').order_by('-id')
            else:
                assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username
                    ).filter(status='Closed').order_by('-id')
            title = 'Closed'
        else:
            assigned_tasks = models.CreateTaskModel.objects.filter(asigned_by__username=request.user.username).order_by('-id')
            title = 'Open/In-Progress Task'

        datas = {
            'assigned_tasks': assigned_tasks,
            'users': users,
            'title': title,
            'task_title_lists': ['Open', 'In-Progress', 'Closed'],
            'result_cnt': assigned_tasks.count(),
            'keyword': keyword,
        }
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteTaskView(View):
    def get(self, request, id, view_name):
        task = models.CreateTaskModel.objects.get(id=id)
        task.delete()
        if view_name == 'your-tasks':
            return redirect('/work-management/your-tasks')
        if view_name == 'assigned-tasks':
            return redirect('/work-management/assigned-tasks')
        return redirect('/work-management/tasks-list')

@method_decorator(login_required(login_url="/"), name='dispatch')
class TaskView(View):
    template_name = 'task-view.html'

    def get(self, request, id):
        try:
            task = models.CreateTaskModel.objects.get(id=id)
            attachments = models.AttachmentModel.objects.filter(task=task)
            datas = {
                'task': task,
                'attachments': attachments,
            }
        except:
            datas = {}
            return redirect('/work-management/tasks-list')
        return render(request, self.template_name, context=datas)

def taskStatusUpdate(request, id, status, view_name):
    try:
        task = models.CreateTaskModel.objects.get(id=id)
        task.status = status
        task.save()
    except Exception as e:
        messages.info(request, f'Error: {e}')

    try:
        if view_name == 'your-tasks':
            return redirect('/work-management/your-tasks')
        if view_name == 'assigned-tasks':
            return redirect('/work-management/assigned-tasks')
        if view_name == 'task-view':
            return redirect(f'/work-management/task-view/{task.id}')
    except: pass
    return redirect('/work-management/tasks-list')

def send_whatsapp_task_twilio(datas):
    client = Client('ACff9de7df66412ff3ce720873c53679e5', '718d5f259973636c24927fbc774dedd3')
    for to_num, subject, priority, url in datas:
        try:
            body_msg = f'New Task\nSubject: {subject}\nPriority: {priority}\nMore Details: {url}'
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=body_msg,
                to=f'whatsapp:{to_num}'
                )
        except: pass

@method_decorator(login_required(login_url="/"), name='dispatch')
class CreateTaskView(View):
    template_name = 'create-task.html'

    def get(self, request, id=None):
        users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin', 'HR'])
        employeers = NewClientModel.objects.all()
        companies_list = AddCompanyModel.objects.all()
        subjects = models.AddSubjectModel.objects.all()
        priority = ['High', 'Medium', 'Low']
        datas = {
                    'users': users, 'priority': priority, 'employeers': employeers,
                    'companies_list': companies_list, 'subjects': subjects,
                }
        if id:
            try:
                task = models.CreateTaskModel.objects.get(id=id)
                datas['task'] = task
            except Exception as e:
                messages.info(request, f'Error: {e}')

        return render(request, self.template_name, context=datas)

    def post(get, request, id=None):
        subject = request.POST.get('subject')
        employer_name = request.POST.get('emp-name')
        company_name = request.POST.get('comp-name')
        priority = request.POST.get('priority')
        asigned_to = request.POST.getlist('asigned_to')
        description = request.POST.get('description')

        if not asigned_to:
            messages.info(request, 'Please select Assigned To..')
            return redirect('/work-management/create-task')

        try:
            employer_name = NewClientModel.objects.get(id=employer_name)
        except Exception:
            employer_name = None

        try:
            company_name = AddCompanyModel.objects.get(id=company_name)
        except Exception:
            company_name = None
        if id:
            try:
                asigned_by = User.objects.get(username=request.user.username)
                edit_task = models.CreateTaskModel.objects.get(id=id)
                subject = models.AddSubjectModel.objects.get(id=subject)
                if edit_task.asigned_by == asigned_by:
                    edit_task.subject = subject
                    edit_task.employer_name = employer_name
                    edit_task.company_name = company_name
                    edit_task.priority = priority
                    edit_task.description = description
                    if request.FILES.get('audio'):
                        edit_task.voice_record = request.FILES.get('audio')
                    edit_task.asigned_to.clear()
                    whats_datas = []
                    if 'All' in asigned_to:
                        users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin', 'HR'])
                        for usr in users:
                            whats_datas.append((usr.phone, subject.subject, priority,
                            f'https://myindiaoverseas.pythonanywhere.com/work-management/task-view/{edit_task.id}'))
                            edit_task.asigned_to.add(usr)
                    else:
                        for assign in asigned_to:
                            asign_to = CreateUserModel.objects.get(user__username=assign)
                            whats_datas.append((usr.phone, subject.subject, priority,
                                f'https://myindiaoverseas.pythonanywhere.com/work-management/task-view/{asign_to.id}'))
                            edit_task.asigned_to.add(asign_to)
                    if request.FILES.getlist('file[]'):
                        att = models.AttachmentModel.objects.filter(task=edit_task)
                        att.delete()
                        for file in request.FILES.getlist('file[]'):
                            attach = models.AttachmentModel(task=edit_task, attachments=file)
                            attach.save()
                    messages.success(request, f'TaskID: {edit_task.id} Edited..')
                else:
                    messages.success(request, f'TaskID: {edit_task.id} Assigned By {edit_task.asigned_by}. Permission Denied (Assigned Your Only Have Edit Permission).')
            except Exception as e:
                messages.info(request, f'Error: {e}')
        else:
            try:
                subject = models.AddSubjectModel.objects.get(id=subject)
                asigned_by = User.objects.get(username=request.user.username)
                create_task = models.CreateTaskModel(subject=subject, employer_name=employer_name,
                                company_name=company_name, asigned_by=asigned_by, priority=priority, description=description,
                                voice_record=request.FILES.get('audio'))
                create_task.save()
                whats_datas = []
                if 'All' in asigned_to:
                    users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin', 'HR'])
                    for usr in users:
                        whats_datas.append((usr.phone, subject.subject, priority,
                        f'https://myindiaoverseas.pythonanywhere.com/work-management/task-view/{create_task.id}'))
                        create_task.asigned_to.add(usr)
                else:
                    for assign in asigned_to:
                        asign_to = CreateUserModel.objects.get(user__username=assign)
                        whats_datas.append((asign_to.phone, subject.subject, priority,
                        f'https://myindiaoverseas.pythonanywhere.com/work-management/task-view/{create_task.id}'))
                        create_task.asigned_to.add(asign_to)

                for file in request.FILES.getlist('file[]'):
                    attach = models.AttachmentModel(task=create_task, attachments=file)
                    attach.save()
                try:
                    send_whatsapp_task_twilio(whats_datas)
                except: pass
                messages.success(request, f'New Task Asigned - {asigned_to}')
            except Exception as e:
                messages.info(request, f'Error: {e}')
        return redirect('/work-management/create-task')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AddSubjectView(View):
    template_name = 'add-subject.html'
    def get(self, request, id=None):
        subjects = models.AddSubjectModel.objects.all()
        datas = {'subjects': subjects}
        if id:
            try:
                datas['subject'] = models.AddSubjectModel.objects.get(id=id)
            except: pass
        return render(request, self.template_name, context=datas)
    def post(self, request, id=None):
        subject = request.POST.get('subject')
        try:
            if id:
                sub = models.AddSubjectModel.objects.get(id=id)
                sub.subject = subject
                sub.save()
                messages.success(request, f'Subject: {subject} Edited..')
            else:
                sub = models.AddSubjectModel(subject=subject)
                sub.save()
                messages.success(request, f'New Subject: {subject} Added..')
        except Exception as e:
            messages.error(request, f'Error : {e}')
        return redirect('/work-management/create-task')

@method_decorator(login_required(login_url="/"), name='dispatch')
class DeleteSubjectView(View):
    def get(self, request, id):
        try:
            subject = models.AddSubjectModel.objects.get(id=id)
            sub_name = subject.subject
            subject.delete()
            messages.success(request, f'{sub_name} Deleted..')
        except: pass
        return redirect('/work-management/create-task')

@method_decorator(login_required(login_url="/"), name='dispatch')
class Employee_PendingReportView(View):
    template_name = 'employee-pending-report.html'
    def count_tasks(self, users, tasks):
        tasks_cnt = {}
        for user in users:
            # usr = tasks.filter(asigned_to=user)
            # asigned_by = [i.asigned_by.username for i in usr.filter(asigned_to__user=user.user)]
            # asigned_by_cnt = { i: asigned_by.count(i) for i in asigned_by}
            # tasks_cnt[user.user.username] = asigned_by_cnt

            op_usr = tasks.filter(asigned_to=user).filter(Q(status='Open')|Q(status__isnull=True))
            op_asigned_by = [i.asigned_by.username for i in op_usr.filter(asigned_to__user=user.user)]
            op_asigned_by_cnt = { i: op_asigned_by.count(i) for i in op_asigned_by}

            ip_usr = tasks.filter(asigned_to=user).filter(status='In-Progress')
            ip_asigned_by = [i.asigned_by.username for i in ip_usr.filter(asigned_to__user=user.user)]
            ip_asigned_by_cnt = { i: ip_asigned_by.count(i) for i in ip_asigned_by}

            if op_asigned_by_cnt and ip_asigned_by_cnt:
                op = {i: f'{op_asigned_by_cnt[i]}' for i in op_asigned_by_cnt }
                ip = {i: f'{ip_asigned_by_cnt[i]}' for i in ip_asigned_by_cnt }
                op_ip_merge = {}
                for i in (op|ip):
                    if i in op and i in ip:
                        op_ip_merge[i] = f'{op[i]} + {ip[i]}'
                    elif i in op:
                        op_ip_merge[i] = f'{op[i]} + 0'
                    elif i in ip:
                        op_ip_merge[i] = f'0 + {ip[i]}'
            else:
                op_ip_merge = {}
                if op_asigned_by_cnt:
                    op_ip_merge = { i: f'{op_asigned_by_cnt[i]} + 0'
                                    for i in op_asigned_by_cnt}
                if ip_asigned_by_cnt:
                    op_ip_merge = { i: f'0 + {ip_asigned_by_cnt[i]}'
                                    for i in ip_asigned_by_cnt}
            tasks_cnt[user.user.username] = op_ip_merge

        return tasks_cnt

    def get(self, request):
        try:
            tasks = models.CreateTaskModel.objects.filter(Q(status__in=['Open', 'In-Progress',])|Q(status__isnull=True))
            users = CreateUserModel.objects.filter(user__groups__name__in=['User', 'Admin'])
            pending_tasks = self.count_tasks(users, tasks)
            users_list = list(pending_tasks)
            if 'admin' not in users_list:
                users_list.append('admin')
            pending_html_table = '''
                            <thead>
                                <tr>
                                    <th style="text-align:center"><strong>EMPLOYEE</strong></th>
                                    <th style="text-align:center"><strong>TOTAL</strong></th>
                                    {}
                                </tr>
                            </thead>
                            <tbody>
                                {}
                            </tbody>
                        '''
            th = '\n'.join([f'<th style="text-align:center"><strong>{usr.upper()}</strong></th>' for usr in users_list])
            tbody = ''
            for p in pending_tasks:
                v = pending_tasks[p]
                r = [eval(v.get(i, '0')) for i in users_list]
                sep_r = [v.get(i, 0) for i in users_list]
                td = f'<tr><td style="text-align:center">{p}</td>\n\
                    <td style="text-align:center">{sum(r)}</td>\n\
                    '
                # td = td+('\n'.join([f'<td style="text-align:center">{i}</td>' if i
                #                         else '<td style="text-align:center">-</td>' for i in sep_r]))+'</tr>'

                for i in sep_r:
                    if i:
                        op, ip = i.split('+')
                        op, ip = op.strip(), ip.strip()
                        td = td + f'<td style="text-align:center"><p title="open" class="badge bg-inverse-primary">{op}</p> + <p title="In-Progress" class="badge bg-inverse-warning">{ip}</p></td>'
                    else:
                        td = td + '<td style="text-align:center">-</td>'

                tbody = tbody + td

            pending_html_table = pending_html_table.format(th, tbody)
            datas = {'html_table': pending_html_table}
        except:
            datas = {}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class EmployeerPendingReportView(View):
    template_name = 'employeer-pending-report.html'
    def get(self, request):
        tasks = models.CreateTaskModel.objects.filter(Q(status__in=['Open', 'In-Progress',])
            |Q(status__isnull=True)).values('employer_name__client_id', 'employer_name__client_name',
            'company_name__company_id', 'company_name__company_name').annotate(
            status_count=Count('company_name')).order_by('company_name__company_name', 'company_name__company_id')
        datas = {'tasks_list': tasks}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class MultiDeleteTaskView(View):
    def post(self, request):
        try:
            task_ids = eval(request.body.decode())['id']
            tasks = models.CreateTaskModel.objects.filter(id__in=task_ids)
            t = tasks.count()
            tasks.delete()
            response_data = {'status': 'success'}
            messages.success(request, f'{t} Task Deleted')
        except Exception as e:
            response_data = {'status': 'error'}
            messages.error(request, f'Error: {e}')
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class FinanceAditListView(View):
    template_name = 'finance-audit-list.html'
    
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
            if keyword.lower().startswith('emp='):
                try:
                    emp = int(keyword.split('=')[-1])
                    companies = models.AddCompanyModel.objects.filter(client__client_id=emp).order_by('client__client_id', 'company_id')
                except:
                    companies = models.AddCompanyModel.objects.all().order_by('client__client_id', 'company_id')
            else:
                companies = AddCompanyModel.objects.filter(Q(company_name__icontains=keyword) |
                    Q(roc__icontains=keyword) | Q(company_review__date_of_incorp__icontains=keyword) |
                    Q(company_review__finance_year_end__icontains=keyword)).order_by('client__client_id', 'company_id')
        else:
            companies = AddCompanyModel.objects.all().order_by('client__client_id', 'company_id')

        columnfilter = request.GET.get('columnfilter')
        if columnfilter is not None:
            companies = companies.filter(
                company_review__finance_year_end__icontains=str(columnfilter)[:2].strip(),
                ).filter(company_review__finance_year_end__icontains=str(columnfilter)[-3:].strip())
            get_url = request.get_full_path()
            if '?columnfilter' in get_url:
                get_url = get_url.split('&page=')[0]
                current_url = f"{get_url}&"
            else:
                get_url = get_url.split('?')[0]
                current_url = f"{get_url}?"
 
        companies_page = Paginator(companies, 25)
        page_number = request.GET.get('page')

        try:
            companies_page = companies_page.get_page(page_number)
        except PageNotAnInteger:
            companies_page = companies_page.page(1)
        except EmptyPage:
            companies_page = companies_page.page(companies_page.num_pages)

        datas = {'companies': companies_page,
                 'result_cnt': companies.count(),
                 'keyword': keyword,
                 'current_url': current_url}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class FinanceAditEditView(View):
    def get(self, request):

        try:
            cellid = request.GET.get('cellid')
            cellvalue = request.GET.get('cellvalue')

            # date_of_incorp column
            if cellid.endswith('date'):
                id = int(cellid.split('_')[0])
                comp = AddCompanyModel.objects.get(id=id)
                comp.company_review.date_of_incorp = cellvalue
                comp.company_review.save()

            # finance_year_end
            elif cellid.endswith('yearend'):
                id = int(cellid.split('_')[0])
                comp = AddCompanyModel.objects.get(id=id)
                comp.company_review.finance_year_end = cellvalue
                comp.company_review.save()

            response_data = {
                'status': 'success',
            }
        except:
            response_data = {
                'status': 'error',
            }
        return JsonResponse(response_data)
    
@method_decorator(login_required(login_url="/"), name='dispatch')
class FinanaceFormulas(View):
    def year_end(self, sdate):
        self.months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
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
        
    def get(self, request):
        companies = CompanyReviewModel.objects.filter(finance_year_end__isnull=False)
        columnname = request.GET.get('columnname')
        result = set()
        for comp in companies:
            try:
                fyear = str(comp.finance_year_end).replace(' ', '').lower()
                r = self.dateParsing(fyear)
                if columnname == 'AgmStart':
                    result.add((fyear, r[0]))
                elif columnname == 'AgmEnd':
                    result.add((fyear, r[1]))
                elif columnname == 'ARStart':
                    result.add((fyear, r[2]))
                elif columnname == 'AREnd':
                    result.add((fyear, r[3]))
                elif columnname == 'AISStart':
                    result.add((fyear, r[4]))
                elif columnname == 'AISEnd':
                    result.add((fyear, r[5]))
                elif columnname == 'FYRStart':
                    result.add((fyear, r[6]))
                elif columnname == 'FYRSEnd':
                    result.add((fyear, r[7]))
                elif columnname == 'YearEnd':
                    result.add((fyear, fyear))
            except Exception as e:
                print('ERROR:', e)
        response_data = {'status': 'success', 'result': sorted(result)}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFTrackerUpdateView(View):
    def get_previous_six_months(self):
        months = {1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL', 5: 'MAY', 6: 'JUNE',
        7: 'JULY', 8: 'AUGUST', 9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'}
        previous_6_months = []
        current_date = datetime.today()
        for _ in range(1, 5):
            prev_month = calendar._prevmonth(current_date.year, current_date.month)
            current_date = datetime(year=prev_month[0], month=prev_month[1], day=1)
            colname = f"{months[prev_month[1]][:3]}{prev_month[0]}"
            previous_6_months.append(colname)

        return previous_6_months[::-1]

    def need_col_parse(self, comp):
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

    def available_col_parse(self, comp):
        '''
            Formula: AVAIL=[FULL+(PART/2)]+[FULL+(PART/2)]+[FULL+(PART/2)]/3
        '''
        prev_3_months = self.get_previous_six_months()[-4:-1]
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

    def get(self, request):
        cellid = request.GET.get('cellid')
        cellvalue = request.GET.get('cellvalue')
        try:
            company_id = int(cellid.split('_')[0])
            comp = AddCompanyModel.objects.get(id=company_id)

            if comp.cpf_tracker and comp.cpf_tracker.monthly_update:
                exist_data = comp.cpf_tracker.monthly_update
                exist_data[cellid] = cellvalue
                comp.cpf_tracker.monthly_update = exist_data
                comp.cpf_tracker.save()
            else:
                cpf_tracker = CPFTrackerCompanyModel(monthly_update={cellid: cellvalue})
                cpf_tracker.save()
                comp.cpf_tracker = cpf_tracker
                comp.save()

            try:
                need_col = self.need_col_parse(comp)
                avail_col = self.available_col_parse(comp)
                if need_col == 0 and avail_col == 0:
                    status_col = ''
                elif need_col > avail_col:
                    status_col = 'Check'
                else:
                    status_col = 'Clear'
                local_count = [need_col, avail_col, status_col]
            except Exception as e:
                local_count = []
            response_data = {'status': 'success', 'compid': comp.id, 'local_count': local_count}
        except:
            response_data = {'status' 'error'}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFTrackerTackingView(View):
    template_name = 'cpf-tracker.html'
    def get_previous_six_months(self):
        months = {1: 'JANUARY', 2: 'FEBRUARY', 3: 'MARCH', 4: 'APRIL', 5: 'MAY', 6: 'JUNE',
        7: 'JULY', 8: 'AUGUST', 9: 'SEPTEMBER', 10: 'OCTOBER', 11: 'NOVEMBER', 12: 'DECEMBER'}
        previous_6_months = []
        current_date = datetime.today()
        for _ in range(1, 5):
            prev_month = calendar._prevmonth(current_date.year, current_date.month)
            current_date = datetime(year=prev_month[0], month=prev_month[1], day=1)
            colname = f"{months[prev_month[1]][:3]}{prev_month[0]}"
            previous_6_months.append(colname)

        return previous_6_months[::-1]

    def filter_json_field(self, col):
        companies_obj = AddCompanyModel.objects.filter(cpf_tracker__monthly_update__isnull=False)
        companies = []
        for comp in companies_obj:
            try:
                d = comp.cpf_tracker.monthly_update
                k = f'{comp.id}_{col}'
                if d[k].lower().strip() == 'yes':
                    companies.append(comp.id)
            except:
                pass
        return companies_obj.filter(id__in=companies)

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
            if keyword.lower().startswith('emp='):
                try:
                    emp = int(keyword.split('=')[-1])
                    companies = models.AddCompanyModel.objects.filter(client__client_id=emp)
                except:
                    companies = models.AddCompanyModel.objects.all()
            elif keyword.lower().endswith('hr_service'):
                try:
                    companies = self.filter_json_field('hr_service')
                except:
                    companies = models.AddCompanyModel.objects.all()
            else:
                companies = AddCompanyModel.objects.filter(Q(company_name__icontains=keyword) |
                                                       Q(roc__icontains=keyword))
        else:
            companies = AddCompanyModel.objects.all()

        companies_page = Paginator(companies, 25)
        page_number = request.GET.get('page')

        try:
            companies_page = companies_page.get_page(page_number)
        except PageNotAnInteger:
            companies_page = companies_page.page(1)
        except EmptyPage:
            companies_page = companies_page.page(companies_page.num_pages)

        datas = {'companies': companies_page,
                 'result_cnt': companies.count(),
                 'keyword': keyword,
                 'current_url': current_url,
                 'previous_months': self.get_previous_six_months()}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFTrackerHRUpdateView(View):
    def get(self, request):
        cellid = request.GET.get('cellid')
        cellvalue = request.GET.get('cellvalue')
        try:
            company_id = int(cellid.split('_')[0])
            comp = AddCompanyModel.objects.get(id=company_id)
            if comp.cpf_tracker and comp.cpf_tracker.hr_info:
                exist_data = comp.cpf_tracker.hr_info
                exist_data[cellid] = cellvalue
                comp.cpf_tracker.hr_info = exist_data
                comp.cpf_tracker.save()
            else:
                if comp.cpf_tracker:

                    hr_info = CPFTrackerCompanyModel(monthly_update=comp.cpf_tracker.monthly_update,
                                                     hr_info={cellid: cellvalue})
                    hr_info.save()
                    comp.cpf_tracker = hr_info
                    comp.save()
            response_data = {'status': 'success'}
        except:
            response_data = {'status' 'error'}
        return JsonResponse(response_data)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CPFTrackerHRTackingView(View):
    template_name = 'cpf_to_hr.html'
    def parse_int(self, d):
        try:
            return int(d)
        except:
            return None
    def get(self, request, id):
        try:
            company = AddCompanyModel.objects.get(id=id)
            cpf_tracker = company.cpf_tracker
            hr_types = []
            if cpf_tracker and cpf_tracker.monthly_update:
                cpf_dict = cpf_tracker.monthly_update
                ep = self.parse_int(cpf_dict.get(f'{company.id}_ep'))
                tep = self.parse_int(cpf_dict.get(f'{company.id}_tep'))
                sp = self.parse_int(cpf_dict.get(f'{company.id}_sp'))
                wp = self.parse_int(cpf_dict.get(f'{company.id}_wp'))
                nts = self.parse_int(cpf_dict.get(f'{company.id}_nts'))
                prc = self.parse_int(cpf_dict.get(f'{company.id}_prc'))
                twp = self.parse_int(cpf_dict.get(f'{company.id}_twp'))

                if ep is not None:
                    for i in range(1, ep+1):
                        hr_types.append(f'EP{i}')
                if tep is not None:
                    for i in range(1, tep+1):
                        hr_types.append(f'TEP{i}')
                if sp is not None:
                    for i in range(1, sp+1):
                        hr_types.append(f'SP{i}')
                if wp is not None:
                    for i in range(1, wp+1):
                        hr_types.append(f'WP{i}')
                if nts is not None:
                    for i in range(1, nts+1):
                        hr_types.append(f'NTS{i}')
                if prc is not None:
                    for i in range(1, prc+1):
                        hr_types.append(f'PRC{i}')
                if twp is not None:
                    for i in range(1, twp+1):
                        hr_types.append(f'TWP{i}')
            datas = {'company': company, 'hrtypes': hr_types}
        except Exception as e:
            datas = {}
        return render(request, self.template_name, context=datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class RenewalTrackerTrackingView(View):
    template_name = 'renewal-tracker.html'
    def convert_str_date(self, dd, mm, yy):
        from datetime import date
        months = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
        # Day Parsing
        try:
            dd = int(dd.strip())
        except:
            dd = None
        # Month Parsing
        try:
            mm = mm.strip()
            if mm.isalpha():
                mm = months[mm[:3].upper()]
            else:
                mm = int(mm)
        except:
            mm = None
        # Year Paring
        try:
            yy = yy.strip()
            if len(yy) == 4:
                yy = int(yy)
            else:
                yy = int(f'20{yy[-2:]}')
        except:
            yy = None

        if all([dd, mm, yy]):
            try:
                return date(day=dd, month=mm, year=yy)
            except Exception as e:
                return None

    def normalize_date(self, sdate):
        try:
            if '-' in sdate:
                dd, mm, yy = sdate.strip().split('-')
                return self.convert_str_date(dd, mm, yy)
            elif '/' in sdate:
                dd, mm, yy = sdate.strip().split('/')
                return self.convert_str_date(dd, mm, yy)
            else:
                dd, mm, yy = sdate.strip().split()
                return self.convert_str_date(dd, mm, yy)
        except Exception as e:
            dd = mm = yy = None

    def parse_hr_info(self, comp):
        from datetime import date
        hr_info = comp.cpf_tracker.hr_info
        hr_details = []
        for hr in hr_info:
            try:
                if hr.endswith('name') and str(hr_info[hr]).strip():
                    passtype = hr.split('_')[1]
                    employee_name = hr_info[hr]
                    if passtype.startswith(('TEP', 'TWP')):
                        continue
                    try:
                        redate = hr_info[f'{comp.id}_{passtype}_canexpiry']
                        if str(redate).strip():
                            continue
                    except: pass
                    try:
                        if hr_info[f'{comp.id}_{passtype}_markasdone']:
                            continue
                    except: pass
                    try:
                        expiry_date = hr_info[f'{comp.id}_{passtype}_expiry']
                        if expiry_date:
                            try:
                                expiry_date = self.normalize_date(expiry_date.strip())
                                expiry_count = (expiry_date - date.today()).days
                            except:
                                expiry_count = ''
                    except:
                        expiry_date = ''
                        expiry_count = ''
                    try:
                        from dateutil.relativedelta import relativedelta
                        re_due_date = expiry_date - relativedelta(months=6)
                        redue_count = (re_due_date - date.today()).days
                    except:
                        re_due_date = ''
                        redue_count = ''

                    remark = hr_info.get(f'{comp.id}_{passtype}_renewal_remark_reason', '')
                    application_no = hr_info.get(f'{comp.id}_{passtype}_renewal_application_no', '')
                    hr_details.append({'company': comp,
                                    'passtype': passtype,
                                    'employeename': employee_name,
                                    'expiry_date': expiry_date,
                                    're_due_date': re_due_date,
                                    'expiry_count': expiry_count,
                                    'expiry_count_bool': isinstance(expiry_count, int),
                                    'redue_count': redue_count,
                                    'remark_reason': remark,
                                    'application_no': application_no})

            except: pass
        return hr_details

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
            if str(keyword).startswith('emp='):
                try:
                    emp = int(keyword.split('=')[-1])
                    companies = AddCompanyModel.objects.filter(client__client_id=emp).filter(cpf_tracker__hr_info__isnull=False)
                except:
                    companies = AddCompanyModel.objects.filter(cpf_tracker__hr_info__isnull=False)
            else:
                companies = AddCompanyModel.objects.filter(cpf_tracker__hr_info__isnull=False)
        else:
            companies = AddCompanyModel.objects.filter(cpf_tracker__hr_info__isnull=False)

        renewal_tracker = []
        for comp in companies:
            try:
                renewal_tracker.extend(self.parse_hr_info(comp))
            except: pass
        try:
            def func(d):
                if d['expiry_count'] == '':
                    return 0
                return d['expiry_count']
            renewal_tracker = sorted(renewal_tracker, key=func)
        except: pass
        try:
            ren_cnt = len(renewal_tracker)
        except:
            ren_cnt = 0
        datas = {'renewal_datas': renewal_tracker, 'reasons': ['Applied', 'Applied Own',
                                                               'Not Workable', 'UnContactable'], 'count': ren_cnt}
        return render(request, self.template_name, context=datas)
