from agent_candidate import models
from job_advertisement.models import MyTodoModel, EmployeerPersonalNotesModel
from datetime import datetime, timedelta
from django.contrib.auth.models import User

def folderslists(request):
    t = datetime.today() + timedelta(hours=5, minutes=30)
    t = datetime.strptime(t.strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
    folders = models.FoldersModel.objects.all()
    title_folders = models.CreateTitleFolderModel.objects.all()
    try:
        user = User.objects.get(username=request.user)
        empnotescnt = EmployeerPersonalNotesModel.objects.filter(user=user,
            status=False, alert_date__lte=datetime.today()).count()
    except:
        empnotescnt = 0
    try:
        todo_cnt = MyTodoModel.objects.filter(user=request.user, deadline__lte=t, is_completed=False).count()
    except:
        todo_cnt = 0
    datas = {'folders': folders, 'title_folders': title_folders, 'todo_cnt': todo_cnt, 'empnotescnt': empnotescnt}
    return datas
