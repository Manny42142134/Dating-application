from django.contrib import admin
from django.urls import path
from .views import register_page, login_page, products, user, update

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', register_page, name='home'), 
    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),
    path('products/', products, name='products'),
    path('user/', user, name='user'),
    path('update/', update, name='update'),
]