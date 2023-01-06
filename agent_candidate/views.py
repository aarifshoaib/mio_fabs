from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from agent_candidate import models
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import django
from datetime import datetime

# git branch -M main
# git push -u origin main

class Login(View):
    template_name = 'login.html'
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        password = request.POST.get('password')

        user = authenticate(username=name, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("/dashboard") 
        else:
            messages.info(request, "Incorrect Username or Password!")
            return redirect('/')

@method_decorator(login_required(login_url="/"), name='dispatch')
class Dashboard(View):
    template_name = 'admin-dashboard.html'
    def get(self, request):
        return render(request, self.template_name)

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
        phone2 = request.POST.get('phone2')
        asigned_to = request.POST.get('asigned_to')

        user = User.objects.get(username=asigned_to)
        asigned_to = models.CreateUserModel.objects.get(user=user)

        if id is not None:
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
                return redirect(f'/agent-candidate/candidate-form/{id}')
        else:
            try:
                reg_form = models.CandidateFormModels(name=name, phone=phone, phone2=phone2, asigned_to=asigned_to)
                reg_form.save()
                messages.success(request, 'Candidate Created Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
        return redirect('/agent-candidate/candidate-form')

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required('agent_candidate.view_candidateformmodels', raise_exception=True), name='dispatch')
class CandidateDetails(View):
    template_name = 'candidate-details.html'
    def get(self, request):
        candidates = models.CandidateFormModels.objects.all()
        candidate_page = Paginator(candidates, 10)
        page_number = request.GET.get('page')
        try:
            candidate_page = candidate_page.get_page(page_number)
        except PageNotAnInteger:
            candidate_page = candidate_page.page(1)
        except EmptyPage:
            candidate_page = candidate_page.page(candidate_page.num_pages)

        return render(request, self.template_name, context={'candidate_page': candidate_page})

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required('agent_candidate.delete_candidateformmodels', raise_exception=True), name='dispatch')
class CandidateDelete(View):
    def get(self, request, id):
        candidate = models.CandidateFormModels.objects.get(id=id)
        candidate.delete()
        return redirect('/agent-candidate/candidate-details')

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
    def get(self, request, id, edit=None):
        countries = models.CountriesListModel.objects.all()
        candidate_detail = {'countries': countries}
        
        if id is not None:
            
            candidate = models.CandidateFormModels.objects.get(id=id)
            candidate_detail['candidate'] = candidate

            agent = models.AgentFormModel.objects.filter(candidate=candidate)
            if agent:
                if agent.first().candidate_dob:
                    candidate_detail['candidate_dob'] = agent.first().candidate_dob.strftime('%Y-%m-%d')
                if agent.first().spouse_dob:
                    candidate_detail['spouse_dob'] = agent.first().spouse_dob.strftime('%Y-%m-%d')
                candidate_detail['countries_list'] = [i.country_name for i in agent.first().country_experience.all()]
                candidate_detail['agent'] = agent.first()
    
        return render(request, self.template_name, context=candidate_detail)

    def post(self, request, id):
        username = request.user
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

        user = User.objects.get(username=username)

        if candidate_dob:
            candidate_dob = datetime.strptime(candidate_dob, '%Y-%m-%d').date()
        if spouse_dob:
            spouse_dob = datetime.strptime(spouse_dob, '%Y-%m-%d').date()

        candidate = models.CandidateFormModels.objects.get(id=id)
        candidate.user = user
        candidate.phone2 = phone2
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
                spouse_highest_edu=spouse_highest_edu,spouse_dob=spouse_dob)
                agent.save()

                for cntry in country_experience:
                    country = models.CountriesListModel.objects.get(country_name=cntry)
                    agent.country_experience.add(country)

                messages.success(request, 'Candidate Details Updated Successfully.')
            except Exception as e:
                messages.info(request, f'{e}')

            return redirect(f'/agent-candidate/agent-form/{id}')
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
                agent.save()

                agent.country_experience.clear()
                for cntry in country_experience:
                    country = models.CountriesListModel.objects.get(country_name=cntry)
                    agent.country_experience.add(country)
                messages.success(request, 'Candidate Edited Successfully.')
            except Exception as e:
                messages.info(request, e)

            return redirect(f'/agent-candidate/agent-form/{id}')
        
@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentDetails(View):
    template_name = 'agent-details.html'
    def get(self, request):
        agents = models.AgentFormModel.objects.filter(is_active=True)
        return render(request, self.template_name, context={'agents': agents})

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentDelete(View):
    def get(self, request, id):
        agent = models.AgentFormModel.objects.get(id=id)
        agent.is_active = False
        agent.save()
        return redirect('agent-details')

@method_decorator(login_required(login_url="/"), name='dispatch')
@method_decorator(permission_required(['agent_candidate.add_createusermodel',
            'agent_candidate.view_createusermodel',
            'agent_candidate.change_createusermodel'], raise_exception=True), name='dispatch')
class CreateUsers(View):
    template_name = 'create-user.html'
    def get(self, request):
        agents = models.CreateUserModel.objects.all()
        agents_datas = {}
        agents_datas['agents'] = agents
        return render(request, self.template_name, context=agents_datas)
    
    def post(self, request):
        user_role = request.POST.get('role')
        user_name = request.POST.get('user-name')
        user_email = request.POST.get('user-email')
        user_password = request.POST.get('password1')
        user_confirm_password = request.POST.get('password2')

        if user_password == user_confirm_password:
            try:
                user = User.objects.create_user(username=user_name, email=user_email, password=user_password)
                user.save()

                group_mod = Group.objects.get(name=user_role)
                group_mod.user_set.add(user)

                a_user = User.objects.get(username=user_name)

                agent_user = models.CreateUserModel(user=a_user, view_password=user_password)
                agent_user.save()
                messages.success(request, f'{user_name} - Created.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'"{user_name}" username. Already Exists!!')
            except Exception as e:
                messages.info(request, e)
        else:
            messages.info(request, 'Password Mismatch!!')

        return redirect('/agent-candidate/create-user')