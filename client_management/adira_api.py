from django.shortcuts import render, redirect
from django.views import View
from client_management import models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import requests

class AdiraOrderListAPI(View):
    def get_file_url(self, fileobj):
        try:
            return f'https://myindiaoverseas.com{fileobj.url}'
        except:
            return None

    def get(self, request):
        orders = models.CreateOrderModel.objects.all()
        datas = {'orders-list': []}
        for order in orders:
            datas['orders-list'].append(
                            {
                            'orderid': order.id, 'order_date': order.order_date, 'require_date': order.require_date,
                            'ref_id': order.ref_id, 'company__company_name': order.company.company_name,
                            'description': order.description, 'pass_type': order.pass_type,
                            'voice_record': self.get_file_url(order.voice_record),
                            'exist_modified_audio': self.get_file_url(order.exist_modified_audio)
                            })
        return JsonResponse(datas)

@method_decorator(login_required(login_url="/"), name='dispatch')
class AdiraLeadsListView(View):
    template_name = 'adira-leads-list.html'

    def get(self, request):
        try:
            adira_url = 'https://adiragroups.com/adira-admin/leads-list-send-mio-team-api/3dd89eff-fb43-4374-9cbd-18d9723c520c'
            res = requests.get(adira_url)
            leads = res.json()
            processed_leads = [i.adira_id for i in models.AdiraProcessedLeadsModels.objects.all()]
            datas = {
                'leads': leads,
                'processed_leads': processed_leads,
            }
        except Exception as e:
            datas = {'leads': []}
        return render(request, self.template_name, context=datas)
    
@method_decorator(login_required(login_url="/"), name='dispatch')
class UpdateAdiraLeadMovedToMIOView(View):
    def post(self, request):
        leadid = request.POST.get('leadid')
        try:
            chk_exist = models.AdiraProcessedLeadsModels.objects.filter(adira_id=leadid)
            if chk_exist:
                adira_lead = models.AdiraProcessedLeadsModels.objects.get(adira_id=leadid)
                adira_lead.delete()
                messages.success(request, f'Lead Moved To UnProcessed Page')
                response_data = {'status': 'success', 'msg': f'Lead Moved To UnProcessed Page'}
            else:
                adira_lead = models.AdiraProcessedLeadsModels(adira_id=leadid)
                adira_lead.save()
                messages.success(request, f'Lead Moved To Processed Page')
                response_data = {'status': 'success', 'msg': f'Lead Moved To Processed Page'}
        except Exception as e:
            messages.error(request, f'Error: {e}')
            response_data = {'status': 'error', 'msg': f'Error: {e}'}
        return JsonResponse(response_data)
