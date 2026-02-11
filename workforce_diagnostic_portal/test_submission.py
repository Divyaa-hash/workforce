import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from diagnostic_app.models import User, JobRole, DiagnosticSubmission
from django.contrib.auth import authenticate

def test_submission():
    # Test user authentication
    print("Testing authentication...")
    user = authenticate(username='founder', password='founder123')
    if user:
        print(f"✅ Authenticated: {user.username} ({user.role})")
    else:
        print("❌ Authentication failed")
    
    # Test job role creation
    print("\nTesting job roles...")
    jobs = JobRole.objects.all()
    print(f"Found {jobs.count()} job roles:")
    for job in jobs:
        print(f"  - {job.title} ({job.budget_range})")
    
    # Test submissions
    print("\nTesting submissions...")
    submissions = DiagnosticSubmission.objects.all()
    print(f"Found {submissions.count()} submissions:")
    for sub in submissions:
        print(f"  - {sub.user.username}: {sub.decision} (Risk: {sub.risk_level})")

if __name__ == "__main__":
    test_submission()