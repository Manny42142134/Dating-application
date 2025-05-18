from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register_page, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('products/', views.products, name='products'),
    path('user/', views.user, name='user'),
    path('update/', views.update, name='update'),
    path('date/', views.date_page, name='date'),
    path('api/profiles/', views.get_profiles, name='get_profiles'),
    path('api/swipe/', views.handle_swipe, name='handle_swipe'),
    path('api/matches/', views.get_matches, name='get_matches'),
    path('api/dummy-users/', views.fetch_dummy_users, name='dummy_users'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/get-messages/', views.get_messages, name='get_messages'),
    path('logout/', views.logout_view, name='logout'),
]