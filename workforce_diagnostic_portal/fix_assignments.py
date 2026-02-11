import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from diagnostic_app.models import User, JobRole, RoleAssignment

def fix_all_assignments():
    print("Fixing all job role assignments...")
    
    # Get all job roles
    job_roles = JobRole.objects.all()
    
    for job in job_roles:
        print(f"\n📋 Processing: {job.title}")
        
        # Get all users
        all_users = User.objects.all()
        
        for user in all_users:
            # Always assign the creator
            if user == job.created_by:
                RoleAssignment.objects.get_or_create(job_role=job, user=user)
                print(f"  ✅ Assigned creator: {user.username}")
            
            # Assign Level 2 users
            elif user.get_level() == 2:
                RoleAssignment.objects.get_or_create(job_role=job, user=user)
                print(f"  ✅ Assigned Level 2: {user.username}")
            
            # Assign Level 3 users
            elif user.get_level() == 3:
                RoleAssignment.objects.get_or_create(job_role=job, user=user)
                print(f"  ✅ Assigned Level 3: {user.username}")
    
    print("\n🎉 All assignments fixed successfully!")
    
    # Show summary
    print("\n📊 Summary:")
    for job in job_roles:
        assignments = RoleAssignment.objects.filter(job_role=job)
        print(f"  {job.title}: {assignments.count()} users assigned")

if __name__ == "__main__":
    fix_all_assignments()