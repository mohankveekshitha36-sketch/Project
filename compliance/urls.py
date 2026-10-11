from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('regulations/', views.RegulationListView.as_view(), name='regulations'),
    path('logs/', views.ActivityLogListView.as_view(), name='logs'),
    path('scan/', views.run_ai_scan, name='run_scan'),
    path('audit-trail/', views.AuditTrailView.as_view(), name='audit_trail'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('staff/', views.StaffManagementView.as_view(), name='staff_mgmt'),
    path('reports-history/', views.ReportsHistoryView.as_view(), name='reports_history'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('signup/', views.SignupView.as_view(), name='signup'),
]
