from django.urls import path
from job_advertisement import views, export_report

urlpatterns = [
    path('create-job', views.CreateJobView.as_view()),
    path('job-list', views.JobListView.as_view()),
    path('job-list/<str:other_url>',views.JobListView.as_view()),
    path('job-review-update/<int:update_review_id>',views.UpdateReviewJob.as_view()),
    path('create-job/<int:id>', views.CreateJobView.as_view()),
    path('delete-job/<int:id>', views.DeleteJobView.as_view()),
    path('job-report-export', export_report.JobReportExportView.as_view()),
    path('companies-report-export', export_report.CompanyReportExportView.as_view()),
    path('my-todo', views.MyTodoView.as_view()),
    path('my-todo-api', views.MyTodoAPIView.as_view()),
    path('completed-todo-api/<int:id>', views.is_completed_todo_api),
    path('delete-todo-api/<int:id>', views.delete_todo_api),
    # Bulk Upload
    path('job-bulk-upload', views.JobBulkUploadView.as_view()),
    path('job-bulk-upload-api', views.InsertJobBulkUploadAPI.as_view()),
    path('access-log', views.UserAccessLogging.as_view()),
    path('active-users', views.ActiveUsersLogView.as_view()),
    path('realtime-active-online-user', views.RealtimeUserOnlineAPI.as_view()),
    path('realtime-active-update-api', views.ActiveUserPageUpdateAPI.as_view()),
    path('staff-maintenance', views.StaffMaintenanceView.as_view()),
    path('staff-maintenance-api', views.staff_maintenance_apiview),
    path('employeer-notes', views.EmployeerPersonalNotesView.as_view()),
    path('employeer-personal-notes-api', views.employeer_personal_notes_api),
    path('update-employeer-personal-notes-api/<int:id>', views.update_employeer_personal_notes_api),
    path('delete-employeer-personal-notes/<int:id>', views.DeleteEmployeerPersonalNotes.as_view()),
    
    path('get-companies-for-employer-api/<int:id>', views.get_companies_for_employer_api),
    path('get_employees_for_company_api/<int:id>', views.get_employer_for_company_api),
]
