from django.urls import path
from client_management import views, adira_api

urlpatterns = [
    # clients
    path('new-client', views.NewClientView.as_view()),
    path('new-client/<int:id>', views.NewClientView.as_view()),
    path('clients-list', views.ClientsListView.as_view()),
    path('client-delete/<int:id>', views.ClientDeleteView.as_view()),
    # companies
    path('add-company', views.AddCompanyView.as_view()),
    path('add-company/<int:id>', views.AddCompanyView.as_view()),
    path('companies-list', views.CompanyListView.as_view()),
    path('company-delete/<int:id>', views.CompanyDeleteView.as_view()),
    path('company-delete/<int:id>/<int:page>', views.CompanyDeleteView.as_view()),
    # view Client
    path('view-client/<int:id>', views.ViewClientView.as_view()),
    path('view-company-delete/<int:id>/<int:client_id>', views.ViewCompanyDeleteView.as_view()),
    path('view-client-companies/<int:id>', views.ViewClientCompaniesView.as_view()),
    # Company Review
    path('company-review-form/<int:id>/<int:page>/<str:return_url>', views.CompanyReviewFormView.as_view()),
    path('company-review-list', views.CompanyReviewListView.as_view()),
    path('company-review-note/<int:id>/<int:page>', views.CompanyReviewNoteView.as_view()),
    # Create Order
    path('create-order-form/<int:id>', views.CreateOrderView.as_view()),
    path('grouped-order-list', views.GroupOrderListView.as_view()),
    path('grouped-order-list/<str:order_key>', views.GroupOrderListView.as_view()),
    path('order-list/<int:id>', views.OrderListView.as_view()),
    path('order-list-overall', views.OrderListOverallView.as_view()),
    path('create-order-form/<int:id>/<int:update_id>', views.CreateOrderView.as_view()),
    path('delete-create-order/<int:id>/<str:pass_type>', views.DeleteCreateOrderView.as_view()),
    path('update-create-order/<int:id>', views.UpdateOrderView.as_view()),
    # Buying & Selling
    path('buying-selling-form', views.BuyingSellingFormView.as_view()),
    path('buying-selling-form/<int:id>/<str:return_url>', views.BuyingSellingFormView.as_view()),
    path('buying-selling-form-api', views.create_buying_selling_api),
    path('buying-selling-form-api/<int:id>/<str:return_url>', views.create_buying_selling_api),
    path('buying-selling-list', views.BuyingSellingListView.as_view()),
    path('delete-buying-selling/<int:id>/<str:return_url>', views.DeleteBuyingSellingView.as_view()),
    path('buyer-form', views.BuyerFormView.as_view()),
    path('buyer-form/<int:id>', views.BuyerFormView.as_view()),
    path('buyer-list', views.BuyerListView.as_view()),
    path('delete-buyer/<int:id>', views.DeleteBuyerView.as_view()),
    path('buyer-info-whatsapp/<int:id>', views.BuyerInfoWhatsapp.as_view()),
    path('seller-info-whatsapp/<int:id>', views.SellerInfoWhatsapp.as_view()),
    # Payslip
    path('approved-emp-payslip/<int:id>', views.ApprovedEmpPayslipView.as_view()),
    path('grouped-companies-payslip', views.GroupedCompaniesPaySlipView.as_view()),
    path('payslip-list/<int:tep_id>', views.PaySlipListView.as_view()),
    path('payslip-generate-api-form/<int:tep_id>', views.CreatePaySlipAPIView.as_view()),
    path('payslip-generate-api-form/<int:tep_id>/<int:id>/<str:return_url>', views.CreatePaySlipAPIView.as_view()),
    path('payslip-generate/<int:id>', views.GeneratePaySlipView.as_view()),
    path('update-payslip/<int:tep_id>/<int:id>/<str:return_url>', views.UpdatePaySlipView.as_view()),
    path('print-payslip/<int:id>/', views.PrintPayslipView.as_view()),
    path('new-candidate-xl-upload', views.AddNewCandidateExcelUpload.as_view()),
    path('new-candidate-xl-upload-api', views.NewCandidateExcelUploadAPI.as_view()),
    path('voice-changer-view', views.VoiceChangerView.as_view()),
    
    # Adira API
    path('adira-orders-list-api', adira_api.AdiraOrderListAPI.as_view()),
    path('adira-leads-list', adira_api.AdiraLeadsListView.as_view()),
    path('update-adira-lead-moved-to-process', adira_api.UpdateAdiraLeadMovedToMIOView.as_view()),
]
