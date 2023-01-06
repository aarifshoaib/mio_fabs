from django.contrib import admin
from django.urls import path
from agent_candidate import views

urlpatterns = [
    path('candidate-form', views.CandidateForm.as_view()),
    path('candidate-form/<int:id>', views.CandidateForm.as_view()),
    path('candidate-details', views.CandidateDetails.as_view()),
    path('candidate-delete/<int:id>', views.CandidateDelete.as_view()),
    path('create-user', views.CreateUsers.as_view()),

    # Agent URLs
    path('agent-form/<int:id>', views.AgentForm.as_view()),
    path('agent-form/<int:id>/<str:edit>', views.AgentForm.as_view()),
    path('agent-details', views.AgentDetails.as_view()),
    path('agent-delete/<int:id>', views.AgentDelete.as_view()),
]