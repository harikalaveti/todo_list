from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from .models import Task
from .forms import TaskForm


def main_view(request):
    """
    Main view that handles everything from a single URL.
    """
    # Handle logout
    if request.GET.get('action') == 'logout':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('main_view')
    
    # Handle user authentication
    if not request.user.is_authenticated:
        login_form = AuthenticationForm()
        register_form = UserCreationForm()
        
        # Handle login
        if request.method == 'POST' and 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect('main_view')
            else:
                messages.error(request, 'Invalid username or password.')
        
        # Handle registration
        elif request.method == 'POST' and 'register' in request.POST:
            print("Registration form submitted")
            print("POST data:", request.POST)
            register_form = UserCreationForm(request.POST)
            print("Form is valid:", register_form.is_valid())
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to your Todo App.')
                return redirect('main_view')
            else:
                print("Form errors:", register_form.errors)
                # Show specific error messages
                error_messages = []
                for field, errors in register_form.errors.items():
                    for error in errors:
                        if field == 'username':
                            error_messages.append(f"Username: {error}")
                        elif field == 'password1':
                            error_messages.append(f"Password: {error}")
                        elif field == 'password2':
                            error_messages.append(f"Confirm Password: {error}")
                        else:
                            error_messages.append(f"{field}: {error}")
                
                if error_messages:
                    for error_msg in error_messages:
                        messages.error(request, error_msg)
                else:
                    messages.error(request, 'Registration failed. Please check your information.')
        
        # Show login/register page
        return render(request, 'todo_app/main.html', {
            'login_form': login_form,
            'register_form': register_form
        })
    
    # User is authenticated - handle task actions
    action = request.GET.get('action')
    task_id = request.GET.get('task_id')
    
    if action == 'add_task' and request.method == 'POST':
        # Handle adding new task
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            if task.reminder_set and not task.reminder_time:
                task.reminder_time = task.due_date - timezone.timedelta(hours=1)
            task.save()
            messages.success(request, 'Task added successfully.')
            return redirect('main_view')
        else:
            messages.error(request, 'Failed to add task. Please check your information.')
    
    elif action == 'mark_completed' and task_id:
        # Handle marking task as completed/incomplete
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        task.completed = not task.completed
        task.save()
        status = "completed" if task.completed else "marked as incomplete"
        messages.success(request, f'Task {status} successfully.')
        return redirect('main_view')
    
    elif action == 'delete_task' and task_id:
        # Handle deleting task
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('main_view')
    
    elif action == 'toggle_reminder' and task_id:
        # Handle toggling reminder
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        task.reminder_set = not task.reminder_set
        if task.reminder_set and not task.reminder_time:
            task.reminder_time = task.due_date - timezone.timedelta(hours=1)
        task.save()
        status = "enabled" if task.reminder_set else "disabled"
        messages.success(request, f'Reminder {status} for task.')
        return redirect('main_view')
    
    # Show task list
    return task_list(request)


@login_required
def task_list(request):
    """
    Display a list of tasks for the logged-in user only.
    """
    # Ensure users can only see their own tasks
    tasks = Task.objects.filter(user=request.user).order_by('completed', 'due_date')
    
    # Add context for overdue and due soon tasks
    now = timezone.now()
    overdue_tasks = [task for task in tasks if task.is_overdue()]
    due_soon_tasks = [task for task in tasks if task.is_due_soon(24) and not task.completed]
    
    context = {
        'tasks': tasks,
        'overdue_tasks': overdue_tasks,
        'due_soon_tasks': due_soon_tasks,
    }
    
    return render(request, 'todo_app/task_list.html', context)


@login_required
def add_task(request):
    """
    Allow user to add a new task with reminder functionality.
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Set reminder time if reminder is enabled but no time specified
            if task.reminder_set and not task.reminder_time:
                # Default reminder: 1 hour before due date
                task.reminder_time = task.due_date - timezone.timedelta(hours=1)
            
            task.save()
            messages.success(request, 'Task added successfully.')
            return redirect('task_list')
    else:
        form = TaskForm()
    
    return render(request, 'todo_app/add_task.html', {'form': form})


@login_required
def update_task(request, pk):
    """
    Allow user to update a task they own with proper security.
    """
    # Ensure user can only update their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            
            # Set reminder time if reminder is enabled but no time specified
            if task.reminder_set and not task.reminder_time:
                task.reminder_time = task.due_date - timezone.timedelta(hours=1)
            
            task.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'todo_app/update_task.html', {'form': form, 'task': task})


@login_required
def delete_task(request, pk):
    """
    Allow user to delete a task they own with proper security.
    """
    # Ensure user can only delete their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully.')
    return redirect('task_list')


@login_required
def mark_completed(request, pk):
    """
    Toggle task completion for a task owned by the user.
    """
    # Ensure user can only modify their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    
    status = "completed" if task.completed else "marked as incomplete"
    messages.success(request, f'Task {status} successfully.')
    return redirect('task_list')


@login_required
def toggle_reminder(request, pk):
    """
    Toggle reminder for a task owned by the user.
    """
    # Ensure user can only modify their own tasks
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.reminder_set = not task.reminder_set
    
    if task.reminder_set and not task.reminder_time:
        # Set default reminder time if not already set
        task.reminder_time = task.due_date - timezone.timedelta(hours=1)
    
    task.save()
    
    status = "enabled" if task.reminder_set else "disabled"
    messages.success(request, f'Reminder {status} for task.')
    return redirect('task_list')
