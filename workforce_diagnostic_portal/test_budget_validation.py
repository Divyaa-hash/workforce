#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from diagnostic_app.forms import JobRoleForm
from diagnostic_app.models import User

# Get a founder user
founder = User.objects.filter(role='founder').first()

# Test different budget formats
test_cases = [
    '3-5 LPA',        # Valid range
    '10 LPA',         # Valid single value
    '18+ LPA',        # Valid with plus
    '7.5-10.5 LPA',   # Valid with decimals
    '4–6 LPA',        # Valid with en dash
    'invalid format', # Invalid
    '0.5 LPA',        # Too low
    '150 LPA',        # Too high
]

base_data = {
    'title': 'Test Budget Job',
    'department': 'Engineering',
    'description': 'Test description',
    'required_skills': 'Python',
    'experience_level': 'Entry Level',
    'urgency': 'medium'
}

print("Testing budget validation:")
print("=" * 50)

for budget in test_cases:
    test_data = base_data.copy()
    test_data['budget_range'] = budget
    
    form = JobRoleForm(data=test_data, user=founder)
    
    print(f"\nBudget: '{budget}'")
    print(f"Valid: {form.is_valid()}")
    
    if not form.is_valid():
        budget_errors = form.errors.get('budget_range', [])
        if budget_errors:
            for error in budget_errors:
                print(f"Error: {error}")
    else:
        print(f"Cleaned budget: '{form.cleaned_data['budget_range']}'")

print("\n" + "=" * 50)
print("Testing salary classification:")
print("=" * 50)

# Test classification
test_salaries = ['2.5 LPA', '5 LPA', '8 LPA', '15 LPA', '25 LPA']

for salary in test_salaries:
    test_data = base_data.copy()
    test_data['budget_range'] = salary
    
    form = JobRoleForm(data=test_data, user=founder)
    if form.is_valid():
        suggested_level = form._classify_by_budget(salary)
        print(f"Salary: {salary} → Suggested Level: {suggested_level}")
