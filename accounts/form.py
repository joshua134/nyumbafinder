import re
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import Role, Profile, AgentCompany
from accounts.utils import encrypt_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username or email',
            'class': 'w-full px-4 py-3 border border-gray-300 text-black placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'w-full px-4 py-3 border border-gray-300 text-black placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.cleaned_data['username'] = username.strip()
        
        return super().clean()

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, )
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Choose a username'})
    )

    class Meta:
        model = User
        fields = ['first_name','last_name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already in use.")
        return email
    
    def clea_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
        
class CompleteProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=18,
        label="Phone number",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. +254712345678, +255712345678, +447123456789',
             'class': 'w-full px-4 py-3 border border-gray-300 text-[var(--text)] placeholder-gray-100 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition '
        })
    )
    
    national_id = forms.CharField(
        max_length=20, 
        label="National/Passport Number",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your National ID or Passport Number',
            'class': 'w-full px-4 py-3 border border-gray-300 text-[var(--text)] placeholder-gray-100 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition '
        })
    )
    role = forms.ModelChoiceField(queryset=Role.objects.all(),
                                  empty_label="Select your role",
                                  widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 text-[var(--text)] rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition laceholder-gray-100 '
        })
    )
   

    class Meta:
        model = Profile
        fields = ['phone','national_id', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].label = "I am a"

        #prefill decrypted data
        if self.instance.pk:
            if self.instance.national_id:
                self.fields['national_id'].initial = self.instance.get_national_id()

    def save(self, commit = True):
        profile = super().save(commit=False)
        
        raw_national_id = self.cleaned_data.get('national_id')
        if raw_national_id:
            profile.national_id = encrypt_data(raw_national_id)

        if commit:
            profile.save()
        return profile
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone
        
        # Remove spaces, dashes, dots, parentheses
        cleaned_phone = re.sub(r'[\s\-\.\(\)]', '', phone)
        
        # Case 1: Already in proper international format (+XXX...)
        if cleaned_phone.startswith('+'):
            if not re.match(r'^\+\d{8,15}$', cleaned_phone):
                raise ValidationError(
                    'Please enter a valid international phone number. '
                    'Example: +254712345678'
                )
            return cleaned_phone
        
        # Case 2: Numbers without + but valid
        elif re.match(r'^\d{8,15}$', cleaned_phone):
            # If it starts with 0, remove it (local format)
            if cleaned_phone.startswith('0'):
                cleaned_phone = cleaned_phone[1:]
            
            # If it's a valid length, add +
            if 8 <= len(cleaned_phone) <= 15:
                return '+' + cleaned_phone
            else:
                raise ValidationError(
                    'Phone number should be between 8-15 digits after country code.'
                )
        
        else:
            raise ValidationError(
                'Please enter a valid phone number. Examples: '
                '+254712345678, 0712345678, 712345678, 254712345678'
            )

class AgentCompanyForm(forms.ModelForm):
    #  Change from HiddenInput to TextInput to make coordinates visible
    latitude = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white text-center font-mono',
            'readonly': True,  # Make it read-only so users can't edit manually
            'placeholder': 'Latitude will appear here'
        })
    )
    longitude = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white text-center font-mono',
            'readonly': True,  # Make it read-only so users can't edit manually
            'placeholder': 'Longitude will appear here'
        })
    )

    class Meta:
        model = AgentCompany
        fields = ['company_name', 'company_address', 'website', 'business_registration', 'latitude', 'longitude']
        widgets = {
            'company_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your complete company address...'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Enter your company name'}),
            'business_registration': forms.TextInput(attrs={'placeholder': 'e.g., CPT/2023/078945'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourcompany.co.ke'}),
        }

    def clean_business_registration(self):
        registration = self.cleaned_data.get('business_registration')
        
        # Exclude the current instance when checking for duplicates
        queryset = AgentCompany.objects.filter(business_registration=registration)
        
        # If we're updating an existing instance, exclude it from the check
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("A company with this registration number already exists.")
        
        return registration
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure latitude and longitude are valid decimal values
        try:
            lat = float(cleaned_data.get('latitude', 0))
            lng = float(cleaned_data.get('longitude', 0))
            
            # Validate latitude range (-90 to 90)
            if lat < -90 or lat > 90:
                self.add_error('latitude', 'Latitude must be between -90 and 90')
            
            # Validate longitude range (-180 to 180)
            if lng < -180 or lng > 180:
                self.add_error('longitude', 'Longitude must be between -180 and 180')
                
        except (ValueError, TypeError):
            self.add_error('latitude', 'Invalid coordinates')
            self.add_error('longitude', 'Invalid coordinates')
        
        return cleaned_data

class ProfileForm(forms.ModelForm):
    # User model fields
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)
        
        # Add profile fields dynamically
        if self.profile_instance:
            self.fields['phone'] = forms.CharField(
                max_length=15,
                required=False,
                initial=self.profile_instance.phone,
                widget=forms.TextInput(attrs={
                    'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
                    'placeholder': '+254712345679'
                })
            )
            

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save profile fields
            if self.profile_instance:
                self.profile_instance.phone = self.cleaned_data.get('phone', '')
                self.profile_instance.county = self.cleaned_data.get('county', '')
                self.profile_instance.town = self.cleaned_data.get('town', '')
                self.profile_instance.estate = self.cleaned_data.get('estate', '')
                self.profile_instance.save()
        return user

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
            'placeholder': 'Current Password'
        }),
        label="Current Password",
        strip=True
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
            'placeholder': 'New Password'
        }),
        label="New Password",
        strip=True
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-[var(--bg)] border border-[var(--border)] rounded-xl px-4 py-3 text-white focus:border-[var(--primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]',
            'placeholder': 'Confirm New Password'
        }),
        label="Confirm New Password",
        strip=True
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not authenticate(username=self.user.username, password=old_password):
            raise ValidationError("Your current password was entered incorrectly. Please enter it again.")
        return old_password
    
    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("The two password fields didn't match.")
        
        # Validate password strength
        if new_password2:
            try:
                validate_password(new_password2, self.user)
            except ValidationError as e:
                raise ValidationError(e.messages)
        
        return new_password2
    
    def save(self):
        """Save the new password"""
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        self.user.save()
        return self.user