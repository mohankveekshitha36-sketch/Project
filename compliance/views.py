from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Regulation, ActivityLog, Violation
from django.db.models import Count, Q
import random
from datetime import datetime, timedelta

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'compliance/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics
        context['total_violations'] = Violation.objects.count()
        context['resolved_violations'] = Violation.objects.filter(status='Resolved').count()
        context['high_severity_alerts'] = Violation.objects.filter(severity='High', status='Pending').count()
        
        # Compliance Score (Simulated: Inverse of violations ratio)
        total_logs = ActivityLog.objects.count()
        if total_logs > 0:
            violation_rate = (context['total_violations'] / total_logs) * 100
            context['compliance_score'] = round(max(0, 100 - violation_rate), 1)
        else:
            context['compliance_score'] = 100.0

        # Data for Charts (Activity over last 7 days)
        last_7_days = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
        context['chart_labels'] = [d.strftime('%b %d') for d in last_7_days]
        context['chart_data'] = [ActivityLog.objects.filter(timestamp__date=d.date()).count() for d in last_7_days]
        
        # Severity Distribution
        context['severity_labels'] = ['Low', 'Medium', 'High']
        context['severity_data'] = [
            Violation.objects.filter(severity='Low').count(),
            Violation.objects.filter(severity='Medium').count(),
            Violation.objects.filter(severity='High').count(),
        ]

        context['recent_violations'] = Violation.objects.all().order_by('-detected_at')[:8]
        context['risk_score'] = 100 - context['compliance_score']
        
        return context

def run_ai_scan(request):
    """
    Enhanced Simulated AI logic with Confidence, Risk Probability, and Reasons.
    """
    logs = ActivityLog.objects.all().order_by('-timestamp')[:50] # Scan recent logs
    regulations = Regulation.objects.all()
    
    if not regulations.exists():
        # Create a default regulation if none exist
        Regulation.objects.create(
            name='General Data Privacy Rule',
            code='GDPR-001',
            description='Access to patient data without valid reason.',
            category='Data Privacy'
        )
        regulations = Regulation.objects.all()

    scanned_count = 0
    detected_count = 0
    
    reasons = [
        "Multiple unauthorized access attempts in a short timeframe.",
        "Resource access outside of standard working hours.",
        "Access to sensitive PHI (Protected Health Information) without active clinical case.",
        "IP address mismatch with user's standard location.",
        "Bulk export of patient records detected.",
        "Potential credential sharing detected between departments."
    ]

    for log in logs:
        if not Violation.objects.filter(activity=log).exists():
            scanned_count += 1
            # 15% chance of detecting a violation for demo simulation
            if random.random() < 0.15:
                reg = random.choice(regulations)
                severity = random.choice(['Low', 'Medium', 'High'])
                confidence = random.uniform(75.0, 99.9)
                risk = random.uniform(60.0, 95.0) if severity == 'High' else random.uniform(20.0, 65.0)
                
                Violation.objects.create(
                    activity=log,
                    regulation=reg,
                    description=f"AI detected suspicious behavior: {log.action} on {log.resource_accessed}.",
                    severity=severity,
                    confidence_score=round(confidence, 1),
                    risk_probability=round(risk, 1),
                    ai_reason=random.choice(reasons)
                )
                detected_count += 1

    return render(request, 'compliance/scan_result.html', {
        'scanned': scanned_count,
        'detected': detected_count
    })

# --- Additional Pages ---

class AuditTrailView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'compliance/audit_trail.html'
    context_object_name = 'logs'
    paginate_by = 50

class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'compliance/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Detailed analytics data
        context['violation_trends'] = [random.randint(2, 10) for _ in range(12)] # Monthly data
        context['top_risks'] = Violation.objects.filter(severity='High').order_by('-confidence_score')[:5]
        return context

class StaffManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'compliance/staff_mgmt.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.models import User
        context['staff_list'] = User.objects.all()
        return context

class ReportsHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'compliance/reports_history.html'

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'compliance/settings.html'

class RegulationListView(LoginRequiredMixin, ListView):
    model = Regulation
    template_name = 'compliance/regulations.html'
    context_object_name = 'regulations'

class ActivityLogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'compliance/logs.html'
    context_object_name = 'logs'
    paginate_by = 20

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
