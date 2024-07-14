# Example URL configuration in myapp/urls.py
from django.urls import path,include
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'),  # Example root path
    path('home/', views.index, name='index'),  # Example root path
    path('chat/', views.chat_assistant_view, name='chat_assistant'),
    # path('admin/', admin.site.urls),

    path('chat_assistant/', views.chat_assistant_view, name='chat_assistant_view'),
    path('clear_history/', views.clear_history, name='clear_history'),
    path('restart_session/', views.restart_session, name='restart_session'),
    
    
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    
    path("about_us", views.about_us, name="about_us"),
    
    # path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),

    
    
    # path('password_reset/', views.password_reset_request, name='password_reset'),
    # path('password_reset_otp/', views.password_reset_otp, name='password_reset_otp'),
    # path('reset/<uidb64>/<otp>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/', views.password_reset, name='password_reset'),

    
    
    path('/activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    
    
]
