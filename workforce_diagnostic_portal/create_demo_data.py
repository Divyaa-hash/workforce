import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from diagnostic_app.models import User, JobRole, RoleAssignment, Notification

def create_demo_data():
    # Create demo job role
    founder = User.objects.get(username='founder')
    
    job, created = JobRole.objects.get_or_create(
        title='Senior Full Stack Developer',
        defaults={
            'department': 'Engineering',
            'description': 'We need a senior developer with expertise in React, Node.js, and cloud technologies to lead our core product development.',
            'required_skills': 'React.js, Node.js, AWS, MongoDB, TypeScript, Docker',
            'experience_level': 'Senior Level (5+ years)',
            'budget_range': '$120k - $150k',
            'urgency': 'high',
            'created_by': founder,
            'status': 'active'
        }
    )
    
    if created:
        print(f"✅ Created job role: {job.title}")
        
        # Auto-assign users
        all_users = User.objects.all()
        for user in all_users:
            RoleAssignment.objects.get_or_create(job_role=job, user=user)
            print(f"   Assigned: {user.username}")
        
        # Create notifications
        for user in all_users:
            Notification.objects.create(
                user=user,
                message=f"You have been assigned to assess the job role: {job.title}",
                job_role=job
            )
        
        print("✅ Created notifications for all users")
    else:
        print(f"⚠️ Job role already exists: {job.title}")
    
    print("\n🎉 Demo data created successfully!")

if __name__ == "__main__":
    create_demo_data()