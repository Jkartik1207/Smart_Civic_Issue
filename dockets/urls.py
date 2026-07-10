from django.urls import path
from . import views

urlpatterns = [
    # Template Pages
    path('', views.index_view, name='index'),
    path('staff/', views.staff_view, name='staff'),
    path('login/', views.login_view, name='login'),
    path('login/admin/', views.admin_login_view, name='admin_login'),
    path('login/labor/', views.labor_login_view, name='labor_login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('labor/', views.labor_view, name='labor'),

    # REST APIs
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/login/admin/', views.api_admin_login, name='api_admin_login'),
    path('api/departments/', views.list_departments, name='api_departments'),
    path('api/issues/', views.list_issues, name='api_list_issues'),
    path('api/issues/create/', views.create_issue, name='api_create_issue'),
    path('api/issues/<int:pk>/upvote/', views.upvote_issue, name='api_upvote_issue'),
    path('api/issues/<int:pk>/status/', views.update_status, name='api_update_status'),
    path('api/issues/<int:pk>/assign/', views.assign_labor, name='api_assign_labor'),
    path('api/labor/location/', views.update_labor_location, name='api_labor_location'),
    path('api/labor/users/', views.list_labor_users, name='api_labor_users'),
]
