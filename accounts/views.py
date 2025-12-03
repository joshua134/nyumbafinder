from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponse
from django.db.models.query_utils import Q
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.backends import EmailOrUsernameModelBackend
from accounts.form import CustomLoginForm, PasswordChangeForm, ProfileForm, RegisterForm, CompleteProfileForm, AgentCompanyForm
from accounts.models import Profile, AgentCompany, CompanyContact
from houses.models import Activity

# accounts/views.py
def custom_login(request):
    if request.user.is_authenticated:
        if not request.user.is_active or not request.user.profile.is_verified and not request.user.profile.is_active:
            messages.error(request, "Your account is inactive or not verified. Please check your email for activation link.")
            return redirect('login')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            print(f"🔍 LOGIN VIEW: Attempting to authenticate '{username}'")
            
            # Try authentication
            user = authenticate(request, username=username, password=password)
            
            print(f"🔍 LOGIN VIEW: Authentication result: {user}")
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Your account is inactive. Please check your email for activation.")
            else:
                print(f"🔍 LOGIN VIEW: Authentication failed for '{username}'")
                messages.error(request, "Invalid username/email or password.")
        else:
            print(f"🔍 LOGIN VIEW: Form invalid - {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# Create your views here.
# 1. REGISTER → SEND EMAIL
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Create empty profile
            Profile.objects.create(user=user)

            # Send activation email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )

            # Send activation email (uncomment when ready)
            """
            send_mail(
                "Activate Your NyumbaFinder KE Account",
                
                Hello {user.first_name},
                
                Welcome to NyumbaFinder KE! Please click the link below to activate your account:
                
                {activation_url}
                
                After activation, you can choose your role (Tenant, Landlord, or Agent).
                
                If you didn't create this account, please ignore this email.
                
                Best regards,
                NyumbaFinder KE Team
                "no-reply@nyumbafinder.co.ke",
                [user.email],
                fail_silently=False,
            )
                """

            # send_mail(
            #     "Activate Your NyumbaFinder KE Account",
            #     f"Click to activate: {activation_url}\n\nAfter activation, choose your role.",
            #     "no-reply@nyumbafinder.co.ke",
            #     [user.email],
            #     fail_silently=False,
            # )

            # TODO: REMOVE PRINT IN PRODUCTION
            print(f"Activation link (for testing): {activation_url}")

            messages.success(request, "Check your email (INBOX/SPAM) for activation link!")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# 2. ACTIVATE ACCOUNT → GO TO CHOOSE ROLE
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Activate user account.
        user.is_active = True
        user.save()

        # update profile
        user.profile.is_verified = True
        user.profile.is_active = True
        user.profile.save()

        # Set the backend attribute on the user
        # user.backend = 'accounts.backends.EmailOrUsernameModelBackend'
        # user.backend = settings.AUTHENTICATION_BACKENDS[0]

        # login user with a specific backend
        backend = EmailOrUsernameModelBackend()
        login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')

        # render success page instead of redirecting.
        return render(request, "accounts/activation_success.html")
    else:
        return render(request, "accounts/activation_invalid.html")
    
# resend activation link
def resend_activation_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active and user.profile.is_verified and user.profile.is_active:
                messages.info(request, "Account is already active. Please sign in.")
                return redirect('login')
            else:
                # Resend activation email
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_url = request.build_absolute_uri(
                    reverse('activate', kwargs={'uidb64': uid, 'token': token})
                )

                print(f"Resend activation link (for testing): {activation_url}")

                # Send activation email (uncomment when ready)
                """
                send_mail(
                    "Activate Your NyumbaFinder KE Account",
                    
                    Hello {user.first_name},
                    
                    Welcome to NyumbaFinder KE! Please click the link below to activate your account:
                    
                    {activation_url}
                    
                    After activation, you can choose your role (Tenant, Landlord, or Agent).
                    
                    If you didn't create this account, please ignore this email.
                    
                    Best regards,
                    NyumbaFinder KE Team
                    "no-reply@nyumbafinder.co.ke",
                    [user.email],
                    fail_silently=False,
                )
                    """

                # send_mail(
                #     "Activate Your NyumbaFinder KE Account",
                #     f"Click to activate: {activation_url}\n\nAfter activation, choose your role.",
                #     "no-reply@nyumbafinder.co.ke",
                #     [user.email],
                #     fail_silently=False,
                # )
                messages.success(request, "Activation email sent! Check your inbox.")
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "No account is found with this email.")
    context = {'support_email': settings.SUPPORT_EMAIL }
    return render(request, 'accounts/resend_activation.html', context)

    # try:
    #     uid = force_str(urlsafe_base64_decode(uidb64))
    #     user = User.objects.get(pk=uid)
    # except:
    #     user = None

    # if user and default_token_generator.check_token(user, token):
    #     user.is_active = True
    #     user.save()
    #     user.profile.is_verified = True
    #     user.profile.save()
    #     login(request, user)
    #     messages.success(request, "Account activated! Now choose your role.")
    #     return redirect('complete_profile')
    # else:
    #     messages.error(request, "Invalid or expired link!")
    #     return redirect('login')

@login_required
def complete_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    # profile = request.user.profile

    if profile.phone and profile.national_id:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile saved successfully.")

            # if profile.user_type == 'agent':
            if profile.role.name == 'agent':
                return redirect('complete_agent_registration')
            else:
                messages.success(request, "Welcome, Landlord! You can now log in and post.")
                return redirect('dashboard')
        else:
            # If form is invalid and profile was just created, delete it
            if created:
                profile.delete()
                messages.error(request, "Please try again with valid information.")
    else:
        form = CompleteProfileForm(instance=profile)

    return render(request, 'accounts/complete_profile.html', {'form': form})

#   initial_roles = [
#         {
#             'name': 'landlord',
#             'description': 'Property owner who rents out properties to tenants'
#         },
#         {
#             'name': 'agent', 
#             'description': 'Real estate agent who manages and sells properties'
#         },
#     ]

@login_required
def complete_agent_registration(request):
    profile = request.user.profile

    if not profile.role or profile.role.name != 'agent': 
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if hasattr(profile, 'company'):
        messages.info(request, "Company already submitted.")
        return redirect('login')

    if request.method == 'POST':
        form = AgentCompanyForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                company = form.save(commit=False)
                company.profile = profile
                company.save()

                # Save multiple contacts
                phones = request.POST.getlist('phones')
                emails = request.POST.getlist('emails')

                for phone in phones:
                    if phone.strip():
                        CompanyContact.objects.create(company=company, contact_type='phone', value=phone.strip())
                for email in emails:
                    if email.strip():
                        CompanyContact.objects.create(company=company, contact_type='email', value=email.strip())

                messages.success(request, "Agent profile created.")
                return redirect('login')
        else:
            messages.error(request, "Make sure your data is correct.")
    else:
        form = AgentCompanyForm()

    return render(request, 'accounts/register_company_details.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'houses': request.user.houses.all().order_by('-date_posted')
    })


@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user, profile_instance=profile)
        if form.is_valid():
            form.save()
            # Create activity for house deletion
            Activity.objects.create(
                user=user,
                activity_type='edit_profile',
                description=f"You have edited your profile.",
                house=None  # No house reference since it's deleted
            )
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
    else:
        form = ProfileForm(instance=user, profile_instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'is_agent': profile.role and profile.role.name == 'agent'  # Add this for the agent check
    })

@login_required
def edit_company(request):
    profile = request.user.profile
    
    # Check if user is an agent and has a company
    if not profile.role or profile.role.name != 'agent' or not hasattr(profile, 'company'):
        messages.error(request, "Access denied or company not found.")
        return redirect('profile')
    
    company = profile.company
    
    if request.method == 'POST':
        # Create a form for editing company details
        form = AgentCompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            
            # Update contacts if needed
            phones = request.POST.getlist('phones')
            emails = request.POST.getlist('emails')
            
            # Delete existing contacts
            company.contacts.all().delete()
            
            # Add new contacts
            for phone in phones:
                if phone.strip():
                    CompanyContact.objects.create(company=company, contact_type='phone', value=phone.strip())
            for email in emails:
                if email.strip():
                    CompanyContact.objects.create(company=company, contact_type='email', value=email.strip())

            Activity.objects.create(
                user=request.user,
                activity_type='edit_company_profile',
                description=f"You have edited company profile.",
                house=None  # No house reference since it's deleted
            )
            
            messages.success(request, "Company information updated successfully.")
            return redirect('profile')
        else:
            print(f"Errors : {form.errors.items()}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}:{error}")
    else:
        form = AgentCompanyForm(instance=company)
        
        contacts = company.contacts.all()
        phones = [c.value for c in contacts if c.contact_type == 'phone']
        emails = [c.value for c in contacts if c.contact_type == 'email']
        
        # Create pairs of phone and email
        contact_pairs = []
        max_length = max(len(phones), len(emails))
        
        for i in range(max_length):
            phone = phones[i] if i < len(phones) else ''
            email = emails[i] if i < len(emails) else ''
            contact_pairs.append((phone, email))
    
    return render(request, 'accounts/edit_company.html', {
        'form': form,
        'contact_pairs': contact_pairs  # Use contact_pairs instead of separate lists
    })

@login_required
@login_required
def change_password(request):
    try:
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, "Your password has been successfully updated!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors below.")
                return render(request, 'accounts/change_password.html', {'form': form})
        
        else:
            form = PasswordChangeForm(request.user)
            return render(request, 'accounts/change_password.html', {'form': form})
            
    except Exception as e:
        print(f"Error in change_password view: {e}")
        messages.error(request, "An error occurred while processing your request. Please try again.")
        
        try:
            form = PasswordChangeForm(request.user)
            return render(request, 'accounts/change_password.html', {'form': form})
        except:
            return redirect('profile')


def password_reset_request(request):
    """
    Handle password reset request (forgot password)
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['email']
            User = get_user_model()
            associated_users = User.objects.filter(Q(email=data))
            
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Request - NyumbaFinder KE"
                    email_template_name = "accounts/password_reset_email.html"
                    context = {
                        "email": user.email,
                        'domain': request.get_host(),
                        'site_name': 'NyumbaFinder KE',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, context)
                    
                    try:
                        send_mail(
                            subject,
                            email,
                            'noreply@nyumbafinder.com',  # Change to your email
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    
                    except Exception as e:
                        print(f"Email sending error: {e}")
                        messages.error(request, "Failed to send email. Please try again.")
                        return render(request, "accounts/password_reset.html", {"form": form})
                
                messages.success(request, "Password reset email sent! Check your inbox.")
                return redirect("password_reset_done")
            
            else:
                # Email doesn't exist in database, but don't reveal that to user
                messages.success(request, "Password reset email sent! Check your inbox.")
                return redirect("password_reset_done")
        
        else:
            messages.error(request, "Please correct the error below.")
    
    else:
        form = PasswordResetForm()
    
    return render(request, "accounts/password_reset.html", {"form": form})

@login_required
def company(request):
    profile = request.user.profile
    
    # Check if user is an agent and has a company
    if not profile.role or profile.role.name != 'agent' or not hasattr(profile, 'company'):
        messages.error(request, "Access denied or company not found.")
        return redirect('profile')
    
    company = profile.company
    return render(request, 'accounts/view_company.html', {'company': company})


def password_reset_done(request):
    """
    Display success message after password reset email is sent
    """
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, uidb64=None, token=None):
    """
    Handle new password entry after reset link is clicked
    """
    # Use Django's built-in view but with our template
    view_class = PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    )
    return view_class(request, uidb64=uidb64, token=token)

def password_reset_complete(request):
    """
    Display success message after password is reset
    """
    return render(request, 'accounts/password_reset_complete.html')
