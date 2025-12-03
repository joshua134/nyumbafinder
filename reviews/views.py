from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from houses.models import House

# Create your views here.


def load_more_reviews(request, id):  # Parameter name must be 'id'
    print(f"load_more_reviews called for house id: {id}")
    
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            house = get_object_or_404(House, id=id, listing_fee_paid=True)
            offset = int(request.GET.get('offset', 0))
            limit = 10

            reviews = house.reviews.all().order_by('-created_at')[offset:offset + limit]
            reviews_data = []

            for review in reviews:
                reviews_data.append({
                    'id': review.id,
                    'name': review.name,
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat(),
                })

            return JsonResponse({
                'success': True,
                'reviews': reviews_data,
                'has_more': house.reviews.count() > offset + limit
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})