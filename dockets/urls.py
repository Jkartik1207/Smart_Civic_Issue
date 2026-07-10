from django.urls import path
from . import views

urlpatterns = [
    # Template Pages
    path('', views.index_view, name='index'),
    path('staff/', views.staff_view, name='staff'),
    path('login/', views.login_view, name='login'),
    path('login/admin/', views.admin_login_view, name='admin_login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # REST APIs
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/login/admin/', views.api_admin_login, name='api_admin_login'),
    path('api/departments/', views.list_departments, name='api_departments'),
    path('api/issues/', views.list_issues, name='api_list_issues'),
    path('api/issues/create/', views.create_issue, name='api_create_issue'),
    path('api/issues/<int:pk>/upvote/', views.upvote_issue, name='api_upvote_issue'),
    path('api/issues/<int:pk>/status/', views.update_status, name='api_update_status'),
]
