from django.urls import path
from . import views
app_name = 'room'
urlpatterns = [
    path('', views.room_index_view, name='room'),
    path('chat/<str:type>', views.room_chat, name='chat'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

]