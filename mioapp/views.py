from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from mioapp import models
from django.contrib import messages
import django

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
            return redirect("/admin-dashboard")
        else:
            messages.info(request, "Incorrect Username or Password!")
            return redirect('/')

@method_decorator(login_required(login_url="/"), name='dispatch')
class AdminDashboard(View):
    template_name = 'admin-dashboard.html'
    def get(self, request):
        return render(request, self.template_name)

@method_decorator(login_required(login_url="/"), name='dispatch')
class CandidateForm(View):
    template_name = 'candidate-form.html'
    def get(self, request, id=None):
        candidate_detail = {}
        if id is not None:
            candidate = models.CandidateForm.objects.get(id=id)
            candidate_detail['candidate'] = candidate
        return render(request, self.template_name, context=candidate_detail)
    
    def post(self, request, id=None):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        if id is not None:
            try:
                reg_form = models.CandidateForm.objects.get(id=id)
                reg_form.name = name
                reg_form.phone = phone
                reg_form.save()
                messages.success(request, 'Candidate Updated Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
                return redirect(f'candidate-form/{id}')
        else:
            try:
                reg_form = models.CandidateForm(name=name, phone=phone)
                reg_form.save()
                messages.success(request, 'Candidate Created Successfully.')
            except django.db.utils.IntegrityError:
                import traceback
                traceback.print_exc()
                messages.info(request, f'{phone} - Already Exists!')
        return redirect('candidate-form')

@method_decorator(login_required(login_url="/"), name='dispatch')
class CandidateDetails(View):
    template_name = 'candidate-details.html'
    def get(self, request):
        candidates = models.CandidateForm.objects.filter(is_active=True)
        return render(request, self.template_name, context={'candidates': candidates})

@method_decorator(login_required(login_url="/"), name='dispatch')
class CandidateDelete(View):
    def get(self, request, id):
        candidate = models.CandidateForm.objects.get(id=id)
        candidate.is_active = False
        candidate.save()
        return redirect('candidate-details')

class AdminLogout(View):
    def get(self, request):
        logout(request)
        return redirect("/")

@method_decorator(login_required(login_url="/"), name='dispatch')
class AgentForm(View):
    template_name = 'agent.html'
    def get(self, request, id=None):
        agent_detail = {}
        if id is not None:
            agent = models.AgentFormModel.objects.get(id=id)
            agent_detail['agent'] = agent
        return render(request, self.template_name, context=agent_detail)

    def post(self, request, id=None):
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        qualification = request.POST.get('qualification')
        passport_no = request.POST.get('passport-no')
        remarks = request.POST.get('remarks')

        if id is not None:
            try:
                agent_form = models.AgentFormModel.objects.get(id=id)
                agent_form.name = name
                agent_form.phone = phone
                agent_form.qualification = qualification
                agent_form.experience = experience
                agent_form.passport_no = passport_no
                agent_form.remarks = remarks
                agent_form.save()
                messages.success(request, 'Candidate Updated Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
                return redirect(f'agent-form/{id}')
            except Exception as e:
                messages.info(request, f'{e}')
                return redirect(f'agent-form/{id}')
        else:
            try:
                agent_form = models.AgentFormModel(name=name, phone=phone, qualification=qualification,
                            experience=experience, passport_no=passport_no, remarks=remarks)
                agent_form.save()
                messages.success(request, 'Candidate Created Successfully.')
            except django.db.utils.IntegrityError:
                messages.info(request, f'{phone} - Already Exists!')
            except Exception as e:
                messages.info(request, f'{e}')
                return redirect(f'agent-form')

        return redirect('agent-form')

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