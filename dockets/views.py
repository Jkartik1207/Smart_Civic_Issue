import json
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Department, Issue, Upvote, LaborProfile
from .serializers import IssueSerializer, DepartmentSerializer, UserSerializer

# Automated routing mapping helper
CATEGORY_TO_DEPT = {
    'pothole': 'Roads',
    'garbage_overflow': 'Sanitation',
    'broken_streetlight': 'Electricity',
    'water_leakage': 'Water Supply'
}

def seed_data_if_empty():
    if Department.objects.exists():
        return

    # Seed departments
    depts = {}
    for cat, dept_name in CATEGORY_TO_DEPT.items():
        dept, _ = Department.objects.get_or_create(name=dept_name, category=cat)
        depts[cat] = dept

    # Create demo citizen user
    demo_citizen, created = User.objects.get_or_create(username='citizen_demo', email='demo@citizen.com')
    if created:
        demo_citizen.set_password('pass123')
        demo_citizen.save()

    # Seed issues
    initial_issues = [
        ('Pothole on Kalawad Road', 'Deep pothole on the service lane, widening after the rains.', 'pothole', 22.3138, 70.7771, 'resolved'),
        ('Overflowing garbage bin', 'Community bin near the market has overflowed for four days.', 'garbage_overflow', 22.2963, 70.7930, 'in_progress'),
        ('Streetlight out', 'Streetlight pole down on University Road stretch, dark at night.', 'broken_streetlight', 22.2911, 70.7818, 'submitted'),
        ('Leaking main line', 'Water main leaking on the road outside Race Course Ring.', 'water_leakage', 22.3050, 70.7901, 'submitted')
    ]

    for title, desc, cat, lat, lng, status_val in initial_issues:
        Issue.objects.create(
            title=title,
            description=desc,
            category=cat,
            latitude=Decimal(str(lat)),
            longitude=Decimal(str(lng)),
            status=status_val,
            department=depts.get(cat),
            reported_by=demo_citizen,
            upvote_count=0
        )

# HTML Page Views
@never_cache
def index_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('staff')
    seed_data_if_empty()
    return render(request, 'dockets/index.html')

@never_cache
@login_required(login_url='/login/admin/')
def staff_view(request):
    if not request.user.is_superuser:
        return redirect('index')
    seed_data_if_empty()
    return render(request, 'dockets/staff.html')

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('staff')
        return redirect('index')
    return render(request, 'dockets/login.html')

@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('staff')
        if hasattr(request.user, 'labor_profile'):
            return redirect('labor')
        return redirect('index')
    return render(request, 'dockets/signup.html')

@never_cache
def admin_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('staff')
        return redirect('index')
    return render(request, 'dockets/admin_login.html')

@never_cache
def labor_login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'is_superuser', False):
            return redirect('staff')
        if hasattr(request.user, 'labor_profile'):
            return redirect('labor')
        return redirect('index')
    return render(request, 'dockets/labor_login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# Django REST Framework API Endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    role = request.data.get('role', 'citizen')
    user = User.objects.create_user(username=username, password=password, email=email)
    
    if role == 'labor':
        LaborProfile.objects.create(user=user)
        
    login(request, user)
    return Response({'success': True, 'user': UserSerializer(user).data})

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        if getattr(user, 'is_superuser', False):
            return Response({'error': 'Superusers must use the admin login portal.'}, status=status.HTTP_403_FORBIDDEN)
        login(request, user)
        return Response({'success': True, 'user': UserSerializer(user).data})
    return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None and getattr(user, 'is_superuser', False):
        login(request, user)
        return Response({'success': True, 'user': UserSerializer(user).data})
    return Response({'error': 'Invalid superuser credentials.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_issues(request):
    # Public route, but can filter/sort issues
    # If request has parameter scope=my and user is authenticated, return only user's issues
    scope = request.query_params.get('scope', '')
    sort_by = request.query_params.get('sort_by', '')
    
    if scope == 'my' and request.user.is_authenticated:
        issues_queryset = Issue.objects.filter(reported_by=request.user)
    else:
        issues_queryset = Issue.objects.all()

    # Apply filters if department is specified
    dept_id = request.query_params.get('department', '')
    if dept_id:
        issues_queryset = issues_queryset.filter(department_id=dept_id)

    # Sort
    if sort_by == 'upvotes':
        issues_queryset = issues_queryset.order_by('-upvote_count', '-created_at')
    else:
        issues_queryset = issues_queryset.order_by('-created_at')

    serializer = IssueSerializer(issues_queryset, many=True, context={'request': request})
    return Response({'issues': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_issue(request):
    title = request.data.get('title')
    description = request.data.get('description')
    photo = request.FILES.get('photo')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    category = request.data.get('category')

    if not title or not latitude or not longitude or not category:
        return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    # Find auto-routing department
    dept_name = CATEGORY_TO_DEPT.get(category)
    department = None
    if dept_name:
        department, _ = Department.objects.get_or_create(name=dept_name, category=category)

    issue = Issue.objects.create(
        title=title,
        description=description,
        photo=photo,
        latitude=Decimal(str(latitude)),
        longitude=Decimal(str(longitude)),
        category=category,
        status='submitted',
        department=department,
        reported_by=request.user,
        upvote_count=0
    )

    return Response({'success': True, 'issue': IssueSerializer(issue, context={'request': request}).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upvote_issue(request, pk):
    try:
        issue = Issue.objects.get(pk=pk)
    except Issue.DoesNotExist:
        return Response({'error': 'Issue not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Toggle upvote
    upvote_qs = Upvote.objects.filter(issue=issue, citizen=request.user)
    if upvote_qs.exists():
        upvote_qs.delete()
        issue.upvote_count = Upvote.objects.filter(issue=issue).count()
        issue.save()
        return Response({'success': True, 'upvoted': False, 'upvote_count': issue.upvote_count})
    else:
        Upvote.objects.create(issue=issue, citizen=request.user)
        issue.upvote_count = Upvote.objects.filter(issue=issue).count()
        issue.save()
        return Response({'success': True, 'upvoted': True, 'upvote_count': issue.upvote_count})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_status(request, pk):
    try:
        issue = Issue.objects.get(pk=pk)
    except Issue.DoesNotExist:
        return Response({'error': 'Issue not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Restricted to superuser or the assigned labor
    if not request.user.is_superuser and issue.assigned_labor != request.user:
        return Response({'error': 'Permissions required.'}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get('status')
    if new_status not in ['submitted', 'in_progress', 'resolved']:
        return Response({'error': 'Invalid status choice.'}, status=status.HTTP_400_BAD_REQUEST)

    issue.status = new_status
    if new_status == 'resolved':
        resolved_photo = request.FILES.get('resolved_photo')
        if resolved_photo:
            issue.resolved_photo = resolved_photo
    issue.save()
    return Response({'success': True, 'status': issue.status})

@api_view(['GET'])
@permission_classes([AllowAny])
def list_departments(request):
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response({'departments': serializer.data})

# Labor APIs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_labor(request, pk):
    if not request.user.is_superuser:
        return Response({'error': 'Admin permissions required.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        issue = Issue.objects.get(pk=pk)
    except Issue.DoesNotExist:
        return Response({'error': 'Issue not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    labor_id = request.data.get('labor_id')
    if labor_id:
        try:
            labor_user = User.objects.get(pk=labor_id)
            if not hasattr(labor_user, 'labor_profile'):
                return Response({'error': 'Selected user is not a labor.'}, status=status.HTTP_400_BAD_REQUEST)
            issue.assigned_labor = labor_user
            issue.status = 'in_progress'
        except User.DoesNotExist:
            return Response({'error': 'Labor user not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        issue.assigned_labor = None
    
    issue.save()
    return Response({'success': True, 'issue': IssueSerializer(issue, context={'request': request}).data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_labor_location(request):
    if not hasattr(request.user, 'labor_profile'):
        return Response({'error': 'Only labor can update location.'}, status=status.HTTP_403_FORBIDDEN)
    
    status_val = request.data.get('status')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    profile = request.user.labor_profile
    if status_val in ['idle', 'working']:
        profile.status = status_val
    if latitude is not None and longitude is not None:
        profile.latitude = Decimal(str(latitude))
        profile.longitude = Decimal(str(longitude))
    
    profile.save()
    return Response({'success': True, 'status': profile.status})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_labor_users(request):
    if not request.user.is_superuser:
        return Response({'error': 'Admin permissions required.'}, status=status.HTTP_403_FORBIDDEN)
    labor_users = User.objects.filter(labor_profile__isnull=False)
    return Response({'labor_users': UserSerializer(labor_users, many=True).data})

@never_cache
@login_required(login_url='/login/')
def labor_view(request):
    if not hasattr(request.user, 'labor_profile'):
        return redirect('index')
    return render(request, 'dockets/labor.html')
