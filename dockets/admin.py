from django.contrib import admin
from .models import Department, Issue, Upvote

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'department', 'reported_by', 'created_at')
    list_filter = ('status', 'category', 'department')
    search_fields = ('title', 'description')

@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ('issue', 'citizen', 'created_at')
    list_filter = ('created_at',)
