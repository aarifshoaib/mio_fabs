import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mio.settings')
django.setup()

from mom_application import models
import imaplib, pytz, re, xlsxwriter
import email, time, email.header, email.utils, traceback
from datetime import datetime, timedelta

# gmail = 'myindiaoverseas.me@gmail.com'
# passwrd = 'melehveeaxbydoce'

import os
from hurry.filesize import size

def get_folder_size(folder_path):
    folders_tracker = {}
    for root, folders, files in os.walk(folder_path):
        for file in files:
            file = os.path.join(root, file)
            if folders_tracker.get(root):
                folders_tracker[root] = folders_tracker[root] + os.stat(file).st_size
            else:
                folders_tracker[root] = os.stat(file).st_size
    sorted_dict = dict(sorted(folders_tracker.items(), key=lambda x: x[1]))
    folders_tracker = {i: size(sorted_dict[i]) for i in sorted_dict}
    print(folders_tracker)

# get_folder_size('/home/myindiaoverseas/mio/media')

def get_server_info():
    from job_advertisement.models import ServerStorageInfoModel
    size_cmd = 'du -hs /home/myindiaoverseas'
    size_info = os.popen(size_cmd).read()
    used_storage = float(size_info.split()[0][:-1])
    total_storage = 40
    percent_used = (used_storage*100)/total_storage

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

# get_server_info()

from mom_application import models

# datas = models.AfterApprovalTEPModel.objects.filter(
#                     workpass__epass_type__icontains='tep')

# for i in datas.filter(workpass__name__icontains='PALANICHAMY'):
#     print(i.workpass.name)
#     print(i.workpass.epass_type)
#     print(i.card_exp)
#     print(i.issue)
#     print(f'"{i.notify_acknowledgement}"')

# from client_management import models

# s = models.BuyingSellingModel.objects.all()
# print(s.count())

t = datetime.today() + timedelta(hours=5, minutes=30)
print(t)