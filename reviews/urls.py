

from django.urls import path
from . import views


urlpatterns = [
    path('reviews/<int:id>/load-more-reviews/', views.load_more_reviews, name='load_more_reviews'),
]