
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about-us/', views.about_view, name='about'),
    path('contact-us/', views.contact_view, name='contact'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('rooms/presidential/', views.p_details_view, name='presidential'),
    path('rooms/twin-delight/', views.twin_details_view, name='delight'),
    path('rooms/contemporary/', views.contem_details_view, name='contemporary'),
    path('rooms/cozy-deluxe/', views.cozy_details_view, name='cozy'),
    path('rooms/diamond/', views.diamond_details_view, name='diamond'),
    path('rooms/gloran-deluxe/', views.deluxe_details_view, name='deluxe'),
    path('rooms/gloran-standard/', views.standard_details_view, name='standard'),
    path('booking/', views.booking_view, name='book'),
]
