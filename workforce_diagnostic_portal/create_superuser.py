import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_root = str(Path(__file__).resolve().parent)
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')

try:
    django.setup()
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    # Check if database is ready
    connection.ensure_connection()
    
    def create_superuser():
        User = get_user_model()
        
        # Superuser details
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'  # Change this to a strong password in production
        
        try:
            # Check if user already exists
            if not User.objects.filter(username=username).exists():
                print("Creating superuser...")
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    role='ceo'  # Set default role, change as needed
                )
                print(f"Superuser created successfully!")
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Email: {email}")
                print("Role: CEO")
                print("\nAccess the admin site at: http://127.0.0.1:8000/admin/")
            else:
                print("Superuser already exists!")
                user = User.objects.get(username=username)
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Role: {user.get_role_display()}")
                
        except Exception as e:
            print(f"Error creating superuser: {str(e)}")
            print("\nMake sure you have run migrations first:")
            print("python manage.py makemigrations")
            print("python manage.py migrate")
    
    if __name__ == "__main__":
        create_superuser()
        
except Exception as e:
    print(f"Error setting up Django: {str(e)}")
    print("\nPlease make sure you're in the correct directory and Django is properly installed.")
    print("Try running these commands first:")
    print("1. python -m pip install -r requirements.txt")
    print("2. python manage.py makemigrations")
    print("3. python manage.py migrate")
