#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from diagnostic_app.forms import JobRoleForm
from diagnostic_app.models import User

# Get a founder user
u = User.objects.filter(role='founder').first()
print(f'Testing with user: {u.username} ({u.role})')

# Test form data
form_data = {
    'title': 'Test Form Job',
    'department': 'Engineering', 
    'description': 'Test description',
    'required_skills': 'Python',
    'experience_level': 'Mid Level',
    'budget_range': '$70k - $90k',
    'urgency': 'medium'
}

# Create and test form
form = JobRoleForm(data=form_data, user=u)
print(f'Form valid: {form.is_valid()}')
print(f'Form errors: {form.errors}')

if form.is_valid():
    print('Form validation passed!')
else:
    print('Form validation failed!')
    for field, errors in form.errors.items():
        print(f'{field}: {errors}')
