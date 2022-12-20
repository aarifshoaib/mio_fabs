from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

class Login(View):
    template_name = 'login.html'
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name')
        password = request.POST.get('password')

        user = authenticate(username=name, password=password)
        print(user)
        
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

class AdminLogout(View):
    def get(self, request):
        logout(request)
        return redirect("/")