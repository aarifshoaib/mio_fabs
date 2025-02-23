from django.urls import path
from mom_application import views

urlpatterns = [
    path('work-pass-status', views.WorkPassStatusView.as_view()),
    path('work-pass-status/<str:page_status>', views.WorkPassStatusView.as_view()),
    path('create-workpass', views.CreateWorkPassView.as_view()),
    path('create-workpass/<int:id>/<str:return_url>', views.CreateWorkPassView.as_view()),
    path('delete-workpass/<int:id>', views.DeleteWorkPassView.as_view()),
    # Upload Pending Doc
    path('upload-pending-doc/<int:id>/<int:page>', views.PendingDocUploadImageView.as_view()),
    path('upload-rejected-doc/<int:id>/<int:page>', views.RejectedReasonDocUploadView.as_view()),
    # Email Tracker
    path('email-list/<int:id>', views.EmailListView.as_view()),
    path('email-credentials', views.EmailCredentialView.as_view()),
    path('add-email-details', views.AddEmailDetailsView.as_view()),
    path('add-email-details/<int:id>', views.AddEmailDetailsView.as_view()),
    path('read-email/<int:id>', views.ReadEmailView.as_view()),
    path('fetch-new-email/<int:id>', views.fetch_new_email),
    path('print-email/<int:id>', views.PrintEmailView.as_view()),
    path('unread-email', views.UnreadMailView.as_view()),
    path('read-all-unread-mails', views.ReadAllUnreadMailsView.as_view()),
    path('read-all-unread-mails/<int:page>', views.ReadAllUnreadMailsView.as_view()),
    # CPF PDF
    path('cpf-invoice', views.CPFExtractView.as_view()),
    path('cpf-list', views.CPFInvoiceList.as_view()),
    path('cpf-files-list/<int:comp_id>', views.CPFFilesList.as_view()),
    path('cpf-invoice-details/<int:id>', views.CPFInvoiceDetails.as_view()),
    path('delete-cpf/<int:id>', views.DeleteCPFInvoice.as_view()),
    path('cpf-entry-form1', views.CPFEntryForm1View.as_view()),
    path('cpf-entry-form1-api', views.CustomerEntryForm1API.as_view()),
    path('cpf-entry-form1-api/<int:id>/<str:return_url>', views.CustomerEntryForm1API.as_view()),
    path('cpf-entry-form1-update/<int:id>/<str:return_url>', views.CPFEntryForm1UpdateView.as_view()),
    path('delete-entry-form1/<int:id>/<str:return_url>', views.DeleteEnterForm1View.as_view()),
    path('cpf-entry-form2', views.CPFEntryForm2View.as_view()),
    path('cpf-entry-form2-api', views.CustomerEntryForm2API.as_view()),
    path('cpf-entry-form2-api/<int:id>/<str:return_url>', views.CustomerEntryForm2API.as_view()),
    path('cpf-entry-form2-update/<int:id>/<str:return_url>', views.CPFEntryForm2UpdateView.as_view()),
    path('delete-entry-form2/<int:id>/<str:return_url>', views.DeleteEnterForm2View.as_view()),
    path('cpf-entry-report', views.CPFEntryReportListView.as_view()),
    # After Approval TEP
    path('after-approval-tep/<int:id>/<str:return_url>', views.AfterApprovalTEPView.as_view()),
    path('after-approved-tep-list', views.AfterApprovedTEPListView.as_view()),
    path('after-approved-tep-list/<str:passtype>', views.AfterApprovedTEPListView.as_view()),
    path('delete-approved-tep/<int:id>', views.DeleteApprovedTEP.as_view()),
    path('delete-uploaded-file-tep/<int:id>/<str:colname>', views.DeleteUploadedTEPFileView.as_view()),
    path('after-issuance-tep', views.AfterIssuanceTEPView.as_view()),
    path('after-issuance-tep/<str:passtype>', views.AfterIssuanceTEPView.as_view()),
    # EPOL Status Checking API
    path('epol-status-checking-api/<int:id>', views.epol_status_check_api),
    # Application Queue
    path('create-app-queue', views.CreateApplicationQueueView.as_view()),
    path('create-app-queue/<int:id>/<str:return_url>', views.CreateApplicationQueueView.as_view()),
    path('app-queue-list', views.ApplicationQueueListView.as_view()),
    path('delete-app-queue/<int:id>/<str:return_url>', views.DeleteAppQueueView.as_view()),
    path('create-app-queue-api', views.create_app_queue_api),
    path('create-app-queue-api/<int:id>/<str:return_url>', views.create_app_queue_api),
    # Reply Email API
    path('reply-email-api/<int:emailtracker_id>', views.ReplyMailAPI.as_view()),
    path('email-search-autocomplete-api/<int:to_mail>/<str:value>', views.search_email_autocomplete),
]
