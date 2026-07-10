from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Issue, Upvote

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'category']

class IssueSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    has_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'photo', 'latitude', 'longitude', 
            'category', 'status', 'department', 'department_name', 
            'reported_by', 'reported_by_username', 'upvote_count', 
            'has_upvoted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'department', 'reported_by', 'upvote_count', 'created_at', 'updated_at']

    def get_has_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Upvote.objects.filter(issue=obj, citizen=request.user).exists()
        return False
