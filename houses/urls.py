from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('search/', views.search, name='search'),  # Search
    path('house/<int:id>/', views.house_detail, name='house_detail'),  # Fixed: <int:id>
    path('post-house/', views.post_house, name='post_house'),  # Post new house
    path('house/<int:house_id>/edit/', views.edit_house, name="edit_house"), # edit house 
    path('house/delete/<int:house_id>/', views.delete_house, name='delete_house'),  # Delete house
    path('house/image/<int:image_id>/delete/', views.delete_house_image, name='delete_house_image'),  # Delete house image
    path('contact-support/<int:house_id>/', views.contact_support, name='contact_support'),
    # path('review/<int:house_id>/', views.add_review, name='add_review'),
    path('house/<int:id>/add-review/', views.house_detail, name='add_review'),
    # Dashboard
    path('dashboard/', views.load_dashboard, name='dashboard'),
    #path('dashboard/', views.dashboard, name='dashboard'),
    #path('dashboard/edit/<int:id>/', views.edit_house, name='edit_house'),
    #path('dashboard/delete/<int:id>/', views.delete_house, name='delete_house'),

    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),  # Privacy Policy
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),  # Terms of Service
    path('how-it-works/', views.how_it_works, name='how_it_works'),  # How It Works
]