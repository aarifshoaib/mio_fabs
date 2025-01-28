import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mio.settings')
django.setup()

from twocaptcha import TwoCaptcha
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from mom_application import models
from datetime import datetime
from django.db.models import Q

api_key = "ed577bb6602bd92c6b08d8f873b7e68b"
solver = TwoCaptcha(api_key)

def captcha_solver(site_key):
    result = solver.recaptcha(sitekey=site_key,
                url='https://service2.mom.gov.sg/workpass/ep/api/foreigner/non-login/get-foreigner',)
    return result, solver.balance()//0.00299

def check_status(datas):
    url = "https://service2.mom.gov.sg/workpass/ep/api/foreigner/non-login/get-foreigner"
    try:
        captcha = captcha_solver(datas['site_key'])
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

def update_workpass_status():
    wp = models.WorkPassModel.objects.filter(Q(status__icontains='pending')|Q(status__icontains='NO_RECORD_FOUND'))
    values = [{'site_key': "6LcUZ3YUAAAAAOWMbxLYrNiFEDnRqk-BgKWqj4gu",
            'objects': {
                'passport_no': data.passport_no, 'dob': data.dob.strftime('%d %B %Y')
            }} for data in wp ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(check_status, value) for value in values]

    current_date, else_block = datetime.today(), False

    for result in as_completed(results):
        result = result.result()
        print(result)
        if result is not None:
            if result.get('success') and type(result.get('results')) == dict:
                pass_no = result['passport_no']
                workpass = models.WorkPassModel.objects.filter(passport_no=pass_no)
                for wp in workpass:
                    wp.status = result['results']['cardData'][0]['cardStatus']
                    wp.last_update = current_date
                    wp.save()
            else:
                pass_no = result['passport_no']
                workpass = models.WorkPassModel.objects.filter(passport_no=pass_no)
                for wp in workpass:
                    wp.error = True
                    wp.status = result['results']
                    wp.save()

    row_cnt = models.CaptchaIssueModel.objects.count()
    if row_cnt == 0:
        sm = models.CaptchaIssueModel(last_update=current_date, balance = solver.balance()//0.00299)
        sm.save()
    else:
        sm = models.CaptchaIssueModel.objects.last()
        sm.last_update = current_date
        sm.balance = solver.balance()//0.00299
        sm.save()

    if not else_block:
        if row_cnt == 0:
            sm = models.CaptchaIssueModel(error=False)
            sm.save()
        else:
            sm = models.CaptchaIssueModel.objects.last()
            sm.error = False
            sm.save()

if __name__ == '__main__':
    print('Fetching Wrokpass Datas. Please wait, it will take sometime')
    update_workpass_status()