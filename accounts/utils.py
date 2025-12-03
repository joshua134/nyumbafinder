from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
import re

fernet = Fernet(settings.FERNET_KEY.encode())

def encrypt_data(text):
    if not text:
        return text
    return fernet.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text):
    if not encrypted_text:
        return encrypted_text
    try:
        return fernet.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return None




def validate_kenyan_id(value):
    """
    Validate Kenyan National ID number
    """
    # Remove any spaces or dashes
    value = str(value).strip().replace(' ', '').replace('-', '')
    
    # Check if it's numeric and within length range
    if not value.isdigit():
        raise ValidationError('Kenyan ID must contain only numbers.')
    
    if len(value) < 8 or len(value) > 12:
        raise ValidationError('Kenyan ID must be between 8-12 digits.')
    
    # Basic checksum validation (simple version)
    if not basic_id_checksum(value):
        raise ValidationError('Invalid Kenyan ID number.')
    
def validate_kenyan_passport(value):
    """
    Validate Kenyan Passport number
    """
    # Remove any spaces or dashes
    value = str(value).strip().replace(' ', '').replace('-', '').upper()
    
    # Passport format: 1-2 letters followed by 6-8 digits
    pattern = r'^[A-Z]{1,2}\d{6,8}$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid Kenyan passport format. Example: A1234567 or AB12345678')

def basic_id_checksum(id_number):
    """
    Basic checksum validation for Kenyan ID
    Note: This is a simplified version
    """
    if len(id_number) != 8:
        return True  # Skip checksum for non-8 digit IDs for now
    
    # Simple algorithm (actual government algorithm is more complex)
    try:
        digits = [int(d) for d in id_number]
        # Weighted sum (simplified)
        weighted_sum = sum(digits[i] * (i + 1) for i in range(7))
        check_digit = weighted_sum % 10
        return check_digit == digits[7]
    except:
        return False