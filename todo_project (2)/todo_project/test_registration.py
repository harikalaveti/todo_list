#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_project.settings')
django.setup()

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

def test_registration():
    print("Testing UserCreationForm validation...")
    
    # Test 1: Valid registration
    print("\n1. Testing valid registration:")
    form_data = {
        'username': 'testuser123',
        'password1': 'ValidPass123!',
        'password2': 'ValidPass123!'
    }
    form = UserCreationForm(form_data)
    print(f"Form valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Errors: {form.errors.as_json()}")
    
    # Test 2: Password too short
    print("\n2. Testing password too short:")
    form_data = {
        'username': 'testuser456',
        'password1': '123',
        'password2': '123'
    }
    form = UserCreationForm(form_data)
    print(f"Form valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Errors: {form.errors}")
    
    # Test 3: Passwords don't match
    print("\n3. Testing passwords don't match:")
    form_data = {
        'username': 'testuser789',
        'password1': 'testpass123',
        'password2': 'differentpass'
    }
    form = UserCreationForm(form_data)
    print(f"Form valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Errors: {form.errors}")
    
    # Test 4: Username already exists
    print("\n4. Testing username already exists:")
    form_data = {
        'username': 'rajesh',  # This user already exists
        'password1': 'testpass123',
        'password2': 'testpass123'
    }
    form = UserCreationForm(form_data)
    print(f"Form valid: {form.is_valid()}")
    if not form.is_valid():
        print(f"Errors: {form.errors}")

if __name__ == '__main__':
    test_registration() 