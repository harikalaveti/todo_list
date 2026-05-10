from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Task


def send_reminders():
    """
    Send reminder emails for tasks that are due soon or overdue.
    This function is called by the cron job.
    """
    now = timezone.now()
    
    # Get tasks that need reminders
    tasks_to_remind = Task.objects.filter(
        reminder_set=True,
        completed=False,
        notified=False,
        reminder_time__lte=now
    )
    
    for task in tasks_to_remind:
        try:
            # Send email reminder
            subject = f'Task Reminder: {task.title}'
            message = f"""
Hello {task.user.username},

This is a reminder for your task: {task.title}

Description: {task.description or 'No description provided'}

Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
Current Time: {now.strftime('%Y-%m-%d %H:%M')}

Please complete this task before the due date.

Best regards,
Your Todo App
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.user.email],
                fail_silently=False,
            )
            
            # Mark as notified to avoid duplicate emails
            task.notified = True
            task.save()
            
            print(f"Reminder sent for task: {task.title} to {task.user.email}")
            
        except Exception as e:
            print(f"Failed to send reminder for task {task.id}: {str(e)}")


def send_overdue_notifications():
    """
    Send notifications for overdue tasks.
    """
    now = timezone.now()
    
    overdue_tasks = Task.objects.filter(
        completed=False,
        due_date__lt=now
    )
    
    for task in overdue_tasks:
        try:
            subject = f'URGENT: Task Overdue - {task.title}'
            message = f"""
Hello {task.user.username},

Your task "{task.title}" is OVERDUE!

Description: {task.description or 'No description provided'}

Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M')}
Current Time: {now.strftime('%Y-%m-%d %H:%M')}

Please complete this task as soon as possible.

Best regards,
Your Todo App
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.user.email],
                fail_silently=False,
            )
            
            print(f"Overdue notification sent for task: {task.title} to {task.user.email}")
            
        except Exception as e:
            print(f"Failed to send overdue notification for task {task.id}: {str(e)}") 