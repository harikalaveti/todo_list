from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.admin.forms import AdminAuthenticationForm
from .models import Task

# Use default admin login form (no custom validation)
# Use default user creation form (no custom validation)

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Due Date and Time',
    )
    
    reminder_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Reminder Date and Time',
        required=False,
        help_text='Set when you want to be reminded about this task'
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'reminder_set', 'reminder_time']

    def clean(self):
        cleaned_data = super().clean()
        due_date = cleaned_data.get('due_date')
        reminder_time = cleaned_data.get('reminder_time')
        reminder_set = cleaned_data.get('reminder_set')

        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Due date cannot be in the past.")

        if reminder_set and reminder_time:
            if reminder_time >= due_date:
                raise forms.ValidationError("Reminder time must be before the due date.")
            if reminder_time < timezone.now():
                raise forms.ValidationError("Reminder time cannot be in the past.")

        return cleaned_data
