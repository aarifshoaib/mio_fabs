from django.urls import path
from work_management import views

urlpatterns = [
    path('tasks-list', views.TasksListView.as_view()),
    path('tasks-list/<str:task_filter>', views.TasksListView.as_view()),
    path('re-assign/<int:id>/<str:view_name>', views.ReAssignTaskView.as_view()),
    path('your-tasks', views.YoursTaskView.as_view()),
    path('delete-task/<int:id>/<str:view_name>', views.DeleteTaskView.as_view()),
    path('assigned-tasks', views.AssignedTaskView.as_view()),
    path('assigned-tasks/<str:task_filter>', views.AssignedTaskView.as_view()),
    path('task-view/<int:id>', views.TaskView.as_view()),
    path('create-task', views.CreateTaskView.as_view()),
    path('create-task', views.CreateTaskView.as_view()),
    path('tasks-list/status-update/<int:id>/<str:status>/<str:view_name>', views.taskStatusUpdate),
    # Edit Created Task
    path('create-task/<int:id>', views.CreateTaskView.as_view()),
    path('add-subject', views.AddSubjectView.as_view()),
    path('add-subject/<int:id>', views.AddSubjectView.as_view()),
    path('delete-subject/<int:id>', views.DeleteSubjectView.as_view()),
    path('employee-pending-report', views.Employee_PendingReportView.as_view()),
    path('employeer-pending-report', views.EmployeerPendingReportView.as_view()),
    path('multi-delete-task-api', views.MultiDeleteTaskView.as_view()),
    # Tracker
    path('finance-audit-list', views.FinanceAditListView.as_view()),
    path('finance-audit-edit', views.FinanceAditEditView.as_view()),
    path('finance-formulas-datas-api', views.FinanaceFormulas.as_view()),

    path('cpf-tracker-tracking-list', views.CPFTrackerTackingView.as_view()),
    path('cpf-tracker-tracking-update', views.CPFTrackerUpdateView.as_view()),
    path('cpf-tracker-hr-tracking-list/<int:id>', views.CPFTrackerHRTackingView.as_view()),
    path('cpf-tracker-hr-tracking-update', views.CPFTrackerHRUpdateView.as_view()),
    path('renewal-tracker', views.RenewalTrackerTrackingView.as_view()),
]
