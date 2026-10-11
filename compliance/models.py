from django.db import models
from django.contrib.auth.models import User

class Regulation(models.Model):
    """
    Stores healthcare regulations like HIPAA, GDPR, etc.
    """
    category_choices = [
        ('Data Privacy', 'Data Privacy'),
        ('Security', 'Security'),
        ('Access Control', 'Access Control'),
        ('Administrative', 'Administrative'),
    ]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=category_choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}: {self.name}"

class ActivityLog(models.Model):
    """
    Records patient data access and other system activities.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patient_id = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    resource_accessed = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} accessed {self.patient_id} at {self.timestamp}"

class Violation(models.Model):
    """
    Detected compliance violations.
    """
    severity_choices = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    status_choices = [
        ('Pending', 'Pending'),
        ('Investigating', 'Investigating'),
        ('Resolved', 'Resolved'),
        ('Dismissed', 'Dismissed'),
    ]
    activity = models.ForeignKey(ActivityLog, on_delete=models.SET_NULL, null=True, blank=True)
    regulation = models.ForeignKey(Regulation, on_delete=models.CASCADE)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=severity_choices)
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')
    
    # AI Specific Fields
    confidence_score = models.FloatField(default=0.0)  # 0.0 to 100.0
    risk_probability = models.FloatField(default=0.0)  # 0.0 to 100.0
    ai_reason = models.TextField(null=True, blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_violations')

    def __str__(self):
        return f"Violation {self.id}: {self.severity} Severity (Conf: {self.confidence_score}%)"
