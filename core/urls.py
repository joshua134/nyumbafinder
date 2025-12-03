"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.contrib.auth import views as auth_views
import accounts.views as account_view

admin.site.site_header = "NyumbaFinder KE - Admin Portal"
admin.site.site_title = "NyumbaFinder Control"
admin.site.index_title = "Welcome Boss - Manage Everything"

def block_admin(request):
    return HttpResponse("Access Denied - This page does not exist", status=403)

urlpatterns = [
    path('', include('houses.urls')),  # homepage
    path('', include('reviews.urls')),  # reviews
    path('', include('payments.urls')),

    # BLOCK DEFAULT ADMIN
    path('admin/', admin.site.urls),

    # SECRET ADMIN URL - ONLY YOU KNOW!
    path('nyumba-secret-panel-2025/', admin.site.urls),  # ← FIXED: NO QUOTES!

    # AUTHENTICATION
    path('register/', account_view.register, name='register'),
    path('login/', account_view.custom_login, name='login'),
    path('activate/<uidb64>/<token>/', account_view.activate, name='activate'),
    path('resend-activation/', account_view.resend_activation_link, name='resend_activation_link'),
    path('complete-profile/', account_view.complete_profile, name='complete_profile'),
    path('complete-agent-registration/', account_view.complete_agent_registration,  name='complete_agent_registration'),
    path('profile/', account_view.profile, name='profile'),
    path('profile/edit/', account_view.edit_profile, name='edit_profile'),
    path('profile/change-password/', account_view.change_password, name='change_password'),
    path('company/edit-company/', account_view.edit_company, name='edit_company'),
    path('company/', account_view.company, name="company"),

    # Password Reset URLs (for logged out users)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # DJANGO BUILT-IN AUTH (login, logout, password reset)
    # path('accounts/', include('django.contrib.auth.urls')),

    # CUSTOM LOGIN & LOGOUT - THIS FIXES THE ERROR!
    # path('login/', auth_views.LoginView.as_view(
    #     template_name='accounts/login.html'
    # ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),

    # YOUR APPS
    # path('dashboard/', include('accounts.urls')),  # landlord dashboard
    # path('payments/', include('payments.urls')),
    # path('reviews/', include('reviews.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# PRODUCTION SECURITY
if not settings.DEBUG:
    urlpatterns = [
                      # path('admin/', block_admin),
                      path('nyumba-secret-panel-2025/', admin.site.urls),
                  ] + urlpatterns
