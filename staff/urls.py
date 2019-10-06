from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.home_view, name='homepage'),
    path('attendance/<str:type>', views.staff_attendance, name='staff-attendance'),
    path('book/<str:type>', views.book, name='book-room'),
    path('checkin/', views.check_in, name='checkin'),
    path('checkout/', views.check_out, name='checkout'),
    path('reservations/', views.reservations, name='reservations'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('inventory/<str:type>', views.inventory, name='inventory'),
    path('create/<str:type>', views.create, name='create'),
    path('room/<str:type>', views.room_management, name='room'),
    path('order/<str:type>', views.order, name='order'),
    path('expenses/<str:type>', views.expenses, name='expenses'),
    path('salary/<str:type>', views.salary, name='salary'),
    path('revenue/<str:type>', views.revenue, name='revenue'),
    path('chat/<str:type>', views.chat, name='chat'),
    path('pcu', views.pcu, name='pcu'),
    path('sm/<str:type>', views.sm, name='sm'),
]