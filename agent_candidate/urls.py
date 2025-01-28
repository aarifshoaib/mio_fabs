from django.urls import path
from agent_candidate import views

urlpatterns = [
    path('candidate-form', views.CandidateForm.as_view()),
    path('candidate-form/<int:id>', views.CandidateForm.as_view()),
    path('candidate-delete/<int:folder_id>/<int:id>', views.CandidateDelete.as_view()),
    path('create-user', views.CreateUsers.as_view()),
    path('create-user/<int:id>', views.CreateUsers.as_view()),
    path('delete-user/<int:id>', views.CreateUserDelete.as_view()),
    path('create-folder/<int:title_id>', views.CreateFolderView.as_view()),
    path('create-folder/<int:title_id>/<int:id>', views.CreateFolderView.as_view()),
    path('delete-folder/<int:title_id>/<int:id>', views.DeleteFolderView.as_view()),
    path('create-title-folder', views.CreateTitleFolderView.as_view()),
    path('create-title-folder/<int:id>', views.CreateTitleFolderView.as_view()),
    path('delete-title-folder/<int:id>', views.DeleteTitleFolderView.as_view()),
    path('folder-link/<int:id>/<int:page>', views.FoldersLinkView.as_view()),
    path('candidate-details', views.CandidateDetails.as_view()),
    path('candidate-details/<int:folder_id>', views.CandidateDetails.as_view()),
    path('candidate-details/<int:folder_id>/<str:back>', views.CandidateDetails.as_view()),
    # Agent URLs
    path('agent-form/<int:id>/<str:back>', views.AgentForm.as_view()),

    # Agent Management
    path('agent-management-new-agent', views.AgentManagementNewAgentView.as_view()),
    path('agent-management-new-agent/<int:id>/<str:return_url>', views.AgentManagementNewAgentView.as_view()),
    path('agent-management-agent-list', views.AgentManagementAgentListView.as_view()),
    path('agent-management-delete-agent/<int:id>/<str:return_url>', views.AgentManagementAgentDeleteView.as_view()),
    path('agent-management-candidate-form', views.AgentManagementCandidateFormView.as_view()),
    path('agent-management-candidate-form/<int:id>/<str:return_url>', views.AgentManagementCandidateFormView.as_view()),
    path('candidate-form-api/', views.candidateform_api),
    path('candidate-form-api/<int:id>/<str:return_url>', views.candidateform_api),
    path('agent-management-candidate-list', views.AgentManagementCandidateListView.as_view()),
    path('agent-management-candidate-list/<str:status>', views.AgentManagementCandidateListView.as_view()),
    path('update-candidate-status/<int:id>/<str:status>/<int:is_remove>', views.UpdateCandidateStatusView.as_view()),
    path('agent-management-candidate-delete/<int:id>', views.AgentManagementCandidateDeleteView.as_view()),
    path('agent-management-delete-file/<int:candidate_id>/<int:id>/<str:return_url>/<str:colname>', views.AgentManagementDeleteFileView.as_view()),
    path('candidate-code-number-update-api/<int:id>/<int:code_value>', views.CanadidateCodeNumberUpdateAPI.as_view()),
    path('agent-candidate-search', views.CandidateSearchView.as_view()),
    path('assign-candidate-to-comp/<int:candid>', views.AssignCandidateToCompanyView.as_view()),
    path('assigned-candidate-lists', views.AssignedCandidateListView.as_view()),
    path('assigned-candidate-view-page/<int:id>', views.AssignedCandidatePageView.as_view()),
    path('read-only-candidate-page/<int:id>/<unique_id>', views.ReadOnlyCandidateView.as_view()),
]