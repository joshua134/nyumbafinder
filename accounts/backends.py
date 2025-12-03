from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either their
    username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"🔍 CUSTOM BACKEND: Attempting authentication for '{username}'")
        if username is None:
            print("🔍 CUSTOM BACKEND: No username provided")
            return None
        
        if password is None:
            return None

        print(f"🔍 AUTHENTICATING: {username}")
        try:
            user = User.objects.get(Q(email__iexact=username) | Q(username__iexact=username) )
            print(f"🔍 USER FOUND: {user.username} (email: {user.email})")
        except User.DoesNotExist:
            print(f"🔍 USER NOT FOUND: {username}")
            return None
        except User.MultipleObjectsReturned:
            print(f"🔍 CUSTOM BACKEND: Multiple users found with username/email: {username}")
            # If multiple users found, try to get the first one that matches password
            users = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            for user in users:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            return None
        
        print(f"🔍 CHECKING PASSWORD...")
        if user.check_password(password) and self.user_can_authenticate(user):
            print(f"🔍 PASSWORD CORRECT")
            print(f"🔍 USER CAN AUTHENTICATE")
            return user
        print(f"🔍 USER CANNOT AUTHENTICATE (inactive or other issue)")
        print(f"🔍 PASSWORD INCORRECT")
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None