import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and print output"""
    print(f"\n🔧 Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode

def main():
    print("🚀 Setting up Workforce Diagnostic Portal...")
    
    # 1. Check Python version
    print("\n📦 Checking Python version...")
    run_command("python --version")
    
    # 2. Install Django and dependencies
    print("\n📦 Installing dependencies...")
    dependencies = [
        "django==4.2.0",
        "pillow==10.0.0",
        "python-dotenv==1.0.0",
    ]
    
    for dep in dependencies:
        run_command(f"pip install {dep}")
    
    # 3. Create required directories
    print("\n📁 Creating directory structure...")
    directories = [
        "static/css",
        "static/js", 
        "static/images",
        "media",
        "diagnostic_app/templates/diagnostic_app",
        "diagnostic_app/templates/diagnostic_app/components",
        "diagnostic_app/management/commands",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created: {directory}")
    
    # 4. Create __init__.py files
    print("\n📄 Creating __init__.py files...")
    init_files = [
        "diagnostic_app/management/__init__.py",
        "diagnostic_app/management/commands/__init__.py",
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write("# Auto-generated\n")
        print(f"Created: {init_file}")
    
    # 5. Create .env file
    print("\n🔐 Creating .env file...")
    with open('.env', 'w') as f:
        f.write('''SECRET_KEY=django-insecure-your-secret-key-here-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
''')
    print("Created: .env")
    
    # 6. Run Django checks
    print("\n✅ Running Django system check...")
    run_command("python manage.py check")
    
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py createsuperuser")
    print("4. Run: python manage.py runserver")
    print("\n🌐 Access at: http://127.0.0.1:8000/")

if __name__ == "__main__":
    main()