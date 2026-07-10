from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Issue, Upvote, LaborProfile

class UserSerializer(serializers.ModelSerializer):
    is_labor = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'is_labor']

    def get_is_labor(self, obj):
        return hasattr(obj, 'labor_profile')

class LaborProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborProfile
        fields = ['status', 'latitude', 'longitude', 'last_location_update']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'category']

class IssueSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    assigned_labor_id = serializers.PrimaryKeyRelatedField(source='assigned_labor', read_only=True)
    assigned_labor_name = serializers.CharField(source='assigned_labor.username', read_only=True)
    assigned_labor_status = serializers.CharField(source='assigned_labor.labor_profile.status', read_only=True)
    assigned_labor_lat = serializers.DecimalField(source='assigned_labor.labor_profile.latitude', max_digits=12, decimal_places=6, read_only=True)
    assigned_labor_lng = serializers.DecimalField(source='assigned_labor.labor_profile.longitude', max_digits=12, decimal_places=6, read_only=True)
    has_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'photo', 'resolved_photo', 'latitude', 'longitude', 
            'category', 'status', 'department', 'department_name', 
            'reported_by', 'reported_by_username', 'assigned_labor',
            'assigned_labor_id', 'assigned_labor_name', 'assigned_labor_status',
            'assigned_labor_lat', 'assigned_labor_lng',
            'upvote_count', 'has_upvoted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'department', 'reported_by', 'assigned_labor', 'upvote_count', 'created_at', 'updated_at']

    def get_has_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Upvote.objects.filter(issue=obj, citizen=request.user).exists()
        return False
