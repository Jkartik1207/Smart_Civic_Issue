from django.db import models
from django.contrib.auth.models import User

class LaborProfile(models.Model):
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('working', 'Working'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='labor_profile')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    latitude = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

class Issue(models.Model):
    CATEGORY_CHOICES = [
        ('pothole', 'Pothole'),
        ('garbage_overflow', 'Garbage Overflow'),
        ('broken_streetlight', 'Broken Streetlight'),
        ('water_leakage', 'Water Leakage'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    photo = models.ImageField(upload_to='issues/', null=True, blank=True)
    resolved_photo = models.ImageField(upload_to='issues/resolved/', null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=6)
    longitude = models.DecimalField(max_digits=12, decimal_places=6)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='issues')
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reported_issues')
    assigned_labor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
    upvote_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.category} ({self.status})"

class Upvote(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='upvotes')
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_upvotes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('issue', 'citizen')

    def __str__(self):
        return f"{self.citizen.username} upvoted {self.issue.title}"
