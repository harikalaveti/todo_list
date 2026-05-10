from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to user account
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()  # for setting deadline
    completed = models.BooleanField(default=False)

    reminder_set = models.BooleanField(default=False)  # whether reminder is enabled
    reminder_time = models.DateTimeField(null=True, blank=True)  # when to send reminder
    notified = models.BooleanField(default=False)  # to avoid duplicate alerts

    def __str__(self):
        return self.title

    def is_overdue(self):
        """Check if task is overdue"""
        return not self.completed and self.due_date < timezone.now()

    def is_due_soon(self, hours=24):
        """Check if task is due within specified hours"""
        if self.completed:
            return False
        now = timezone.now()
        return now <= self.due_date <= now + timezone.timedelta(hours=hours)

    class Meta:
        ordering = ['due_date']  # tasks ordered by upcoming due dates
