from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Department, Issue, Upvote, LaborProfile

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

@admin.register(LaborProfile)
class LaborProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'last_location_update')
    list_filter = ('status',)
    search_fields = ('user__username',)

class LaborProfileInline(admin.StackedInline):
    model = LaborProfile
    can_delete = False
    verbose_name_plural = 'Labor Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (LaborProfileInline, )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
