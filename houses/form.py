
from django import forms

from houses.models import House, HouseImage
from reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'comment', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 text-black rounded-xl border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition',
                'placeholder': 'Enter your name (or stay anonymous)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 text-black rounded-xl border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition',
                'placeholder': 'your@email.com (optional)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 text-black rounded-xl border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition resize-none',
                'rows': 4,
                'placeholder': 'Share your experience with this property...'
            }),
            'rating': forms.HiddenInput(),  # We handle this with JavaScript
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['name'].required = False


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file = super().clean(data, initial)
        if not single_file:
            return []
        return data  # Return the list of files

class HouseForm(forms.ModelForm):
    latitude = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-custom coordinates-display',
            'readonly': True,
            'step': 'any'
        })
    )
    
    longitude = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-custom coordinates-display', 
            'readonly': True,
            'step': 'any'
        })
    )

    class Meta:
        model = House
        fields = [
            'title',
            'house_type', 
            'description',
            'location',
            'rent', 
            'deposit', 
            'house_number', 
            'floor_number',
            'latitude',   
            'longitude',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': 'e.g., Cozy 2-Bedroom Apartment in Westlands'
            }),
            'house_type': forms.Select(attrs={
                'class': 'form-control text-white  form-control-custom'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control text-white  form-control-custom',
                'rows': 4,
                'placeholder': 'Describe your house features, amenities, neighborhood...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control text-white  form-control-custom',
                'placeholder': 'e.g., Ongata Rongai, Kajiado'
            }),
            'rent': forms.NumberInput(attrs={
                'class': 'form-control  text-white form-control-custom',
                'placeholder': '15000',
                'min': '0',
                'step': '100'
            }),
            'deposit': forms.NumberInput(attrs={
                'class': 'form-control text-white  form-control-custom',
                'placeholder': '15000',
                'min': '0', 
                'step': '100'
            }),
            'house_number': forms.TextInput(attrs={
                'class': 'form-control  text-white form-control-custom',
                'placeholder': 'A5'
            }),
            'floor_number': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': '2nd Floor or Ground Floor'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make sure latitude and longitude are submitted
        self.fields['latitude'].widget.attrs['readonly'] = True
        self.fields['longitude'].widget.attrs['readonly'] = True

        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control form-control-custom'


class HouseEditForm(forms.ModelForm):
    latitude = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-custom coordinates-display',
            'readonly': True,
            'step': 'any'
        })
    )
    
    longitude = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=6,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-custom coordinates-display', 
            'readonly': True,
            'step': 'any'
        })
    )

    class Meta:
        model = House
        fields = [
            'title',
            'house_type', 
            'description',
            'location',
            'rent', 
            'deposit', 
            'house_number', 
            'floor_number',
            'latitude',   
            'longitude',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': 'e.g., Cozy 2-Bedroom Apartment in Westlands'
            }),
            'house_type': forms.Select(attrs={
                'class': 'form-control text-white form-control-custom'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control text-white form-control-custom',
                'rows': 4,
                'placeholder': 'Describe your house features, amenities, neighborhood...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': 'e.g., Ongata Rongai, Kajiado'
            }),
            'rent': forms.NumberInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': '15000',
                'min': '0',
                'step': '100'
            }),
            'deposit': forms.NumberInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': '15000',
                'min': '0', 
                'step': '100'
            }),
            'house_number': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': 'A5'
            }),
            'floor_number': forms.TextInput(attrs={
                'class': 'form-control text-white form-control-custom',
                'placeholder': '2nd Floor or Ground Floor'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make latitude and longitude readonly but ensure they're submitted
        self.fields['latitude'].widget.attrs['readonly'] = True
        self.fields['longitude'].widget.attrs['readonly'] = True

        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control form-control-custom'
    
    def clean_latitude(self):
        """Ensure latitude is within valid range for Kenya - More lenient for editing"""
        latitude = self.cleaned_data.get('latitude')
        # More lenient validation for editing existing houses
        if latitude and (latitude < -10.0 or latitude > 10.0):
            raise forms.ValidationError("Please provide a valid latitude for Kenya")
        return latitude
    
    def clean_longitude(self):
        """Ensure longitude is within valid range for Kenya - More lenient for editing"""
        longitude = self.cleaned_data.get('longitude')
        # More lenient validation for editing existing houses
        if longitude and (longitude < 25.0 or longitude > 45.0):
            raise forms.ValidationError("Please provide a valid longitude for Kenya")
        return longitude