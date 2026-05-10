from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'due_date', 'completed', 'reminder_set')
    list_filter = ('completed', 'reminder_set', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'due_date'
    ordering = ('due_date',)

admin.site.register(Task, TaskAdmin)
