import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from compliance.models import Regulation, ActivityLog, Violation

class Command(BaseCommand):
    help = 'Populates the database with realistic premium dummy data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Refreshing premium demo data...')
        
        # Cleanup existing data to avoid duplicates
        Violation.objects.all().delete()
        ActivityLog.objects.all().delete()

        # 1. Create Admin & Staff Users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@hospital.com', 'admin123')
        
        staff_user, _ = User.objects.get_or_create(username='staff_jsmith', defaults={'email': 'smith@hospital.com'})
        staff_user.set_password('staff123')
        staff_user.save()

        # 2. Create Regulations
        regs_data = [
            ('HIPAA Privacy Rule', 'HIPAA-P', 'Protects individuals\' medical records and other personal health information.', 'Data Privacy'),
            ('HIPAA Security Rule', 'HIPAA-S', 'Sets national standards for protecting electronic PHI.', 'Security'),
            ('GDPR Health Data', 'GDPR-H', 'Regulations for processing health data under European law.', 'Data Privacy'),
            ('Access Control Policy', 'ACP-01', 'Standards for clinical systems authentication.', 'Access Control'),
        ]
        
        reg_objs = []
        for name, code, desc, cat in regs_data:
            reg, _ = Regulation.objects.get_or_create(code=code, defaults={'name': name, 'description': desc, 'category': cat})
            reg_objs.append(reg)

        # 3. Create Activity Logs (Last 14 days)
        actions = ['Viewed Patient Record', 'Updated Medical History', 'Accessed Lab Results', 'Discharged Patient', 'Prescribed Medication']
        resources = ['Electronic Health Record (EHR)', 'Patient Portal', 'Laboratory Information System', 'Pharmacy Database']
        patients = ['P-10023', 'P-10554', 'P-20091', 'P-99231', 'P-44512']
        
        logs = []
        for i in range(150):
            days_ago = random.randint(0, 13)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            log = ActivityLog.objects.create(
                user=staff_user,
                patient_id=random.choice(patients),
                action=random.choice(actions),
                resource_accessed=random.choice(resources),
                ip_address=f"192.168.1.{random.randint(2, 254)}"
            )
            ActivityLog.objects.filter(id=log.id).update(timestamp=timestamp)
            logs.append(log)

        # 4. Create realistic Violations with AI Metrics
        reasons = [
            "Multiple unauthorized access attempts in a short timeframe.",
            "Resource access outside of standard working hours.",
            "Access to sensitive PHI without active clinical case.",
            "IP address mismatch with user's standard location.",
            "Bulk export of patient records detected.",
            "Potential credential sharing detected between departments."
        ]

        for i in range(15):
            log = random.choice(logs)
            if not Violation.objects.filter(activity=log).exists():
                reg = random.choice(reg_objs)
                severity = random.choice(['Low', 'Medium', 'High'])
                confidence = random.uniform(75.0, 99.0)
                risk = random.uniform(65.0, 98.0) if severity == 'High' else random.uniform(15.0, 60.0)
                
                Violation.objects.create(
                    activity=log,
                    regulation=reg,
                    description=f"AI detected suspicious behavior: {log.action}.",
                    severity=severity,
                    status=random.choice(['Pending', 'Investigating', 'Resolved']),
                    confidence_score=round(confidence, 1),
                    risk_probability=round(risk, 1),
                    ai_reason=random.choice(reasons),
                    detected_at=log.timestamp + timedelta(minutes=5)
                )

        self.stdout.write(self.style.SUCCESS('Successfully refreshed premium demo data!'))
