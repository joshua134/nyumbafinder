from decimal import Decimal
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

User = get_user_model()

from houses.form import HouseEditForm, ReviewForm, HouseForm
from houses.models import Activity, House, HouseImage, HouseTerm


# Create your views here.
def home(request):
    houses = House.objects.filter(is_active=True,payment_status='paid').order_by('-date_posted')
    
    # handle search
    search_query = request.GET.get('search', '')
    if search_query:
        houses = houses.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(location__icontains=search_query) |
            Q(house_type__icontains=search_query) | Q(rent__icontains=search_query) | Q(floor_number__icontains=search_query)
        )

    # handle sorting
    sort_options = request.GET.get('sort', '')
    if sort_options in ['date_posted', '-date_posted', 'rent', '-rent', 'title', '-title']:
        houses = houses.order_by(sort_options)
    else:
        houses = houses.order_by('-date_posted')

    # handle house type filter
    house_type_filter = request.GET.get('house_type', '')
    if house_type_filter:
        houses = houses.filter(house_type=house_type_filter)

    # handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'approved':
        houses = houses.filter(is_active=True)
    elif status_filter == 'pending':
        houses = houses.filter(is_active=False)

    # handle rent range filter
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')
    
    if min_rent and max_rent:
        houses = houses.filter(rent__gte=Decimal(min_rent), rent__lte=Decimal(max_rent))

    if  min_rent:
        houses = houses.filter(rent__gte=Decimal(min_rent))
    if  max_rent:
        houses = houses.filter(rent__lte=Decimal(max_rent))
    
    # paginatio - 20 houses per page
    paginator = Paginator(houses, 5)
    page = request.GET.get('page', 1)

    try:
        houses_page = paginator.page(page)
    except PageNotAnInteger:
        houses_page = paginator.page(1)
    except EmptyPage:
        houses_page = paginator.page(paginator.num_pages)

    
    context = {
        'houses': houses_page,
        'paginator': paginator,
        'page_obj': houses_page,
        'house_count': houses.count(),
        'is_paginated': houses_page.has_other_pages(),
    }

    # add existing GET parameters to context for pagination links
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    context['get_params'] = get_params.urlencode()
    
    return render(request, 'house/index.html', context)

def search(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')

    houses = House.objects.filter(is_active=True)

    if query:
        houses = houses.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
        )

    if location:
        houses = houses.filter(location__icontains=location)

    return render(request, 'house/search.html', {'houses':houses, 'query':query, 'location': location})


def house_detail(request, id):
    house = get_object_or_404(House, id=id, is_active=True)

    print(f" House : {house} ")

    # reviews = house.reviews.all().order_by('-date_posted')
    reviews = house.reviews.all().order_by('-created_at')[0:10] # Load first review initially
    
    if request.method == 'POST':
        if 'review' in request.POST:
            
            recaptcha_response = request.POST.get('g-recaptcha-response')
            
            if not recaptcha_response:
                messages.error(request,"Please complete your CAPTCHA!")
                return redirect('house_detail', id=id)

            # 2. VERIFY WITH GOOGLE
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            data = { 'secret':settings.RECAPTCHA_SECRET_KEY,
                     'response': recaptcha_response,
                     'remoteip': request.META.get("REMOTE_ADDR")
                    }

            try:
                response = requests.post(verify_url, data=data, timeout=10)
                
                result = response.json()
            
                if not result.get('success'):
                    messages.error(request, "CAPTCHA failed. Are you a robot?")
                    return redirect('house_detail', id=id)

                # 3. CHECK SCORE threshold
                score = result.get('score', 0)
                if score < settings.RECAPTCHA_REQUIRED_SCORE:
                    messages.error(request, "CAPTCHA score too low. Are you a robot?")
                    return redirect('house_detail', id=id)

            except requests.exceptions.RequestException as e:
                messages.error(request, "Error verifying CAPTCHA. Please try again.")
                return redirect('house_detail', id=id)

            review_form = ReviewForm(request.POST)
            
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.house = house
                review.save()
                
                Activity.objects.create(
                    user=None,
                    activity_type='added_review',
                    description=f"A review was added to the house: {house.title}",
                    house=house
                )

                messages.success(request, "Thank you! Your review helps thousands of Kenyans.")
                return redirect('house_detail', id=id)
            else:
                return messages.error(request, "Please correct the errors in your review.")

    review_form = ReviewForm()
    context = {
        'house': house,
        'reviews': reviews,
        'review_form': review_form,
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
    }
    return render(request, 'house/house_detail.html', context)


@login_required
def load_dashboard(request):
    # Check if profile exists without creating it
    has_profile = hasattr(request.user, 'profile')
    
    houses = House.objects.filter(
        owner=request.user
    ).order_by('-date_posted')

    # handle search
    search_query = request.GET.get('search', '')
    if search_query:
        houses = houses.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(location__icontains=search_query) |
            Q(house_type__icontains=search_query) | Q(rent__icontains=search_query) | Q(floor_number__icontains=search_query)
        )

    # handle sorting
    sort_options = request.GET.get('sort', '')
    if sort_options in ['date_posted', '-date_posted', 'rent', '-rent', 'title', '-title']:
        houses = houses.order_by(sort_options)
    else:
        houses = houses.order_by('-date_posted')

    # handle house type filter
    house_type_filter = request.GET.get('house_type', '')
    if house_type_filter:
        houses = houses.filter(house_type=house_type_filter)

    # handle payment status filter (NEW)
    payment_status_filter = request.GET.get('payment_status', '')
    if payment_status_filter:
        houses = houses.filter(payment_status=payment_status_filter)
        if payment_status_filter == 'paid':
            houses = houses.filter(is_active=True)

    # handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'approved':
        houses = houses.filter(is_active=True)
    elif status_filter == 'pending':
        houses = houses.filter(is_active=False)


    # handle listing activity filter (NEW)
    activity_filter = request.GET.get('activity', '')
    if activity_filter == 'active':
        houses = houses.filter(is_active=True)
    elif activity_filter == 'inactive':
        houses = houses.filter(is_active=False)

    # handle rent range filter
    min_rent = request.GET.get('min_rent', '')
    max_rent = request.GET.get('max_rent', '')
    
    if min_rent and max_rent:
        houses = houses.filter(rent__gte=Decimal(min_rent), rent__lte=Decimal(max_rent))

    if  min_rent:
        houses = houses.filter(rent__gte=Decimal(min_rent))
    if  max_rent:
        houses = houses.filter(rent__lte=Decimal(max_rent))

    # paginatio - 20 houses per page
    paginator = Paginator(houses, 5)
    page = request.GET.get('page', 1)

    try:
        houses_page = paginator.page(page)
    except PageNotAnInteger:
        houses_page = paginator.page(1)
    except EmptyPage:
        houses_page = paginator.page(paginator.num_pages)   

    # get recent activities 
    recent_activities = Activity.objects.filter(user=request.user).select_related("house").order_by('-created_at')[:5]
    total_listed_houses = houses.count()
    total_approved_houses = houses.filter(is_active=True).count()

    # Get house types for filter dropdown - ADD THIS LINE
    house_types = House.HOUSE_TYPES
    
    context = {
        'has_profile': has_profile,
        'profile': request.user.profile if has_profile else None,
        'houses': houses_page,
        'recent_activities': recent_activities,
        'total_listed_houses': total_listed_houses,
        'total_approved_houses': total_approved_houses,
        'house_types': house_types,
        'paginator': paginator,
        'page_obj': houses_page,
        'house_count': houses.count(),
        'is_paginated': houses_page.has_other_pages(),
        'amount': settings.AMOUNT_TO_PAY_PER_HOUSE,
    }

    # add existing GET parameters to context for pagination links
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    context['get_params'] = get_params.urlencode()

    return render(request, 'house/dashboard.html', context)


@login_required
def delete_house(request, house_id):
    house = get_object_or_404(House, id=house_id)
    
    # Security check - only owner can delete
    if house.owner != request.user:
        messages.error(request, "You can only delete your own houses!")
        return redirect('dashboard')
    
    if request.method == 'POST':
        house_title = house.title
        house.delete()
        
        # Create activity for house deletion
        Activity.objects.create(
            user=request.user,
            activity_type='deleted_house',
            description=f"You edited the house: {house_title}",
            house=None  # No house reference since it's deleted
        )

        messages.success(request, f'House "{house_title}" has been deleted successfully.')
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
@transaction.atomic
def post_house(request):
    # Check if user has a profile and is verified (adjust based on your profile model)
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        if not profile.is_verified:
            messages.error(request, "Your account is not verified. Complete verification first.")
            return redirect('complete_profile')

    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 1. VALIDATE IMAGES BEFORE CREATING HOUSE
                images = request.FILES.getlist('imageFiles')
                if not images:
                    messages.error(request, "Please upload at least one image.")
                    return render(request, 'house/post_house.html', {
                        'form': form
                    })
                
                if len(images) > 15:
                    messages.error(request, "Maximum 15 images allowed.")
                    return render(request, 'house/post_house.html', {
                        'form': form
                    })

                # Validate each image
                for img in images:
                    # Check file size (20MB = 20 * 1024 * 1024 bytes)
                    if img.size > 20 * 1024 * 1024:
                        messages.error(request, f"Image {img.name} is too large. Maximum size is 20MB.")
                        return render(request, 'house/post_house.html', {
                            'form': form
                        })
                    
                    # Check if it's a valid image using Pillow
                    try:
                        # Open image with Pillow to validate
                        image = Image.open(img)
                        image.verify()  # Verify it's a valid image
                        
                        # Reset file pointer after verification
                        img.seek(0)
                        
                        # Check dimensions (optional)
                        width, height = image.size
                        if width > 10000 or height > 10000:
                            messages.error(request, f"Image {img.name} dimensions are too large.")
                            return render(request, 'house/post_house.html', {
                                'form': form
                            })
                            
                    except Exception as e:
                        messages.error(request, f"Invalid image file: {img.name}. Please upload valid images only.")
                        return render(request, 'house/post_house.html', {
                            'form': form
                        })

                # 2. CREATE HOUSE WITH COORDINATES
                house = form.save(commit=False)
                house.owner = request.user
                #house.is_active = True  # Set to True after payment
                
                # Get coordinates from form
                latitude = form.cleaned_data.get('latitude')
                longitude = form.cleaned_data.get('longitude')
                
                if latitude and longitude:
                    house.latitude = Decimal(latitude)
                    house.longitude = Decimal(longitude)
                
                house.save()

                # 3. SAVE VALIDATED IMAGES
                for img in images:
                    HouseImage.objects.create(
                        house=house, 
                        image=img
                    )

                # 4. SAVE RICH TEXT TERMS FROM QUILL
                terms_content = request.POST.get('terms', '').strip()
                print(f"Received terms content: '{terms_content}'")  # Debug print
                print(f"Terms content length: {len(terms_content)}")  # Debug print
                print(f"All POST data: {dict(request.POST)}")  # Debug print all form data
                
                if not terms_content or terms_content in ['<p><br></p>', '']:
                    messages.error(request, "Please enter at least one rental term.")
                    house.delete()  # Delete the house since terms are invalid
                    return render(request, 'house/post_house.html', {
                        'form': form
                    })

                # Extract plain text from HTML (Quill output)
                soup = BeautifulSoup(terms_content, 'html.parser')
                text = soup.get_text(separator='\n').strip()

                # Split into individual terms (by line)
                term_lines = [line.strip() for line in text.split('\n') if line.strip()]
                print(f"Extracted term lines: {term_lines}") 
                if not term_lines:
                    messages.error(request, "Please enter valid terms.")
                    house.delete() # Delete teh house since terms are invalid.
                    return render(request, 'house/post_house.html', {
                        'form': form
                    })

                # Save each line as a separate HouseTerm
                for term_text in term_lines:
                    # Truncate if longer than 2000 characters
                    if len(term_text) > 2000:
                        term_text = term_text[:1997] + "..."
                    
                    HouseTerm.objects.create(
                        house=house,
                        term=term_text
                    )

                Activity.objects.create(
                    user=request.user,
                    activity_type='posted_house',
                    description=f"You added a  house: {house.title}",
                    house=house
                )

                messages.success(request, "House submitted successfully!")
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error submitting house: {str(e)}")
                return render(request, 'house/post_house.html', {
                    'form': form
                })
        else:
            # Form is invalid, show errors
            messages.error(request, "Please correct the errors below.")
    else:
        # GET request - initialize form with default coordinates
        form = HouseForm(initial={
            'latitude': -1.2921,
            'longitude': 36.8219,
        })

    return render(request, 'house/post_house.html', {
        'form': form
    })

@login_required
def edit_house(request, house_id):
    request.user = User.objects.get(id=request.user.id)
    house = get_object_or_404(House, id=house_id)
    
    if house.owner != request.user:
        messages.error(request, "You can only edit your own houses!")
        return redirect('dashboard')

    terms_html = ""
    if house.terms.exists():
        terms_html = "".join([f"<p>{term.term}</p>" for term in house.terms.all()])
    
    if request.method == 'POST':
        form = HouseEditForm(request.POST, request.FILES, instance=house)
        if form.is_valid():
            try:
                # Save the main house form first
                house = form.save()

                # Handle new images
                new_images = request.FILES.getlist('new_images')
                if new_images:
                    # Check total images won't exceed 15
                    current_count = house.images.count()
                    if current_count + len(new_images) > 15:
                        messages.error(request, f"You can only have 15 images total. You currently have {current_count} images.")
                        return render(request, 'house/edit_house.html', {
                            'form': form, 
                            'house': house, 
                            'terms_html': terms_html,
                        })
                    
                    for img in new_images:
                        # Validate image size
                        if img.size > 20 * 1024 * 1024:  # 20MB
                            messages.error(request, f"Image {img.name} is too large. Maximum size is 20MB.")
                            return render(request, 'house/edit_house.html', {
                                'form': form, 
                                'house': house, 
                                'terms_html': terms_html,
                            })
                        HouseImage.objects.create(house=house, image=img)

                # Handle updated terms (from Quill editor)
                new_terms_html = request.POST.get('terms', '')
                if new_terms_html.strip():
                    # Delete old terms
                    house.terms.all().delete()
                    # Save new terms
                    from django.utils.html import strip_tags
                    clean_text = strip_tags(new_terms_html).strip()
                    if clean_text:
                        # Split by paragraphs and create separate terms
                        terms_list = new_terms_html.split('</p><p>')
                        for term_html in terms_list:
                            clean_term = strip_tags(term_html).strip()
                            if clean_term and clean_term not in ['', '<br>']:
                                HouseTerm.objects.create(house=house, term=clean_term)

                Activity.objects.create(
                    user=request.user,
                    activity_type='edited_house',
                    description=f"You edited the house: {house.title}",
                    house=house
                )

                messages.success(request, "House updated successfully!")
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error updating house: {str(e)}")
                print(f"Error in edit_house: {str(e)}")
        else:
            print("FORM ERRORS:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        
        form = HouseForm(instance=house)

    return render(request, 'house/edit_house.html', {'form': form, 'house': house, 'terms_html': terms_html,})

@login_required
def delete_house_image(request, image_id):
    image = get_object_or_404(HouseImage, id=image_id)
    
    # Security: Only owner of the house can delete images
    if image.house.owner != request.user:
        messages.error(request, "You can only delete images from your own houses!")
        return redirect('dashboard')
    
    if request.method == 'POST':
        house = image.house
        image.image.delete(save=False)  # Delete file from storage
        image.delete()  # Delete DB record

        Activity.objects.create(
            user=request.user,
            activity_type='deleted_house',
            description=f"You delete an image of this house: {house.title}",
            house=None  # No house reference since it's deleted
        )

        messages.success(request, "Image deleted successfully.")
    
    return redirect('edit_house', id=image.house.id)

@login_required
def contact_support(request, house_id):
    from django.core.mail import send_mail
    house = get_object_or_404(House, id=house_id)
    # Prepare email
    subject = f"Payment issue for House {house.id}"
    message = f"""
        Hello Support Team,

        The following house has a verified payment but is inactive:

        House ID: {house.id}
        Title: {house.title}
        Owner: {house.user.get_full_name()}
        Amount Paid: KES {house.rent}

        Please check and activate the listing.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.SUPPORT_EMAIL],
        fail_silently=False,
    )

    # Optionally: add a success message
    from django.contrib import messages
    messages.success(request, "Support has been notified about this listing.")

    # Redirect back to the page user came from
    return redirect(request.META.get('HTTP_REFERER', '/'))

def privacy_policy(request):
    return render(request, 'legal/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'legal/terms_of_service.html')

def how_it_works(request):
    return render(request, 'operations/how_it_works.html')