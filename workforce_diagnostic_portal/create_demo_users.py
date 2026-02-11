import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_demo_users():
    demo_users = [
        {
            'username': 'founder',
            'password': 'founder123',
            'email': 'founder@example.com',
            'role': 'founder',
        },
        {
            'username': 'co_founder',
            'password': 'cofounder123',
            'email': 'cofounder@example.com',
            'role': 'co_founder',
        },
        {
            'username': 'ceo',
            'password': 'ceo123',
            'email': 'ceo@example.com',
            'role': 'ceo',
        },
        {
            'username': 'cto',
            'password': 'cto123',
            'email': 'cto@example.com',
            'role': 'cto',
        },
        {
            'username': 'coo',
            'password': 'coo123',
            'email': 'coo@example.com',
            'role': 'coo',
        },
        {
            'username': 'project_head',
            'password': 'project123',
            'email': 'project@example.com',
            'role': 'project_head',
        },
        {
            'username': 'hr_manager',
            'password': 'hr123',
            'email': 'hr@example.com',
            'role': 'hr_manager',
        },
        {
            'username': 'recruiter',
            'password': 'recruiter123',
            'email': 'recruiter@example.com',
            'role': 'recruiter',
        },
        {
            'username': 'hr_executive',
            'password': 'hrexec123',
            'email': 'hrexec@example.com',
            'role': 'hr_executive',
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in demo_users:
        try:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'is_staff': False,
                    'is_superuser': False
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                print(f"✅ Created: {user.username} ({user.role})")
                created_count += 1
            else:
                # Update password if exists
                user.set_password(user_data['password'])
                user.role = user_data['role']
                user.email = user_data['email']
                user.save()
                print(f"↻ Updated: {user.username} ({user.role})")
                updated_count += 1
                
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {e}")
    
    print(f"\n🎉 Summary: Created {created_count}, Updated {updated_count} users")
    print("\n📋 Demo Credentials:")
    print("-" * 40)
    for user_data in demo_users[:3]:  # Show first 3 for reference
        print(f"👤 {user_data['username']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Role: {user_data['role']}")
        print()

if __name__ == "__main__":
    create_demo_users()