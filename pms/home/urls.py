from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('login_user/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('activation-countdown/', views.activation_countdown, name='activation_countdown'),
    path('save_password/', views.save_password, name='save_password'),
    path('save_photo/', views.save_photo, name='save_photo'),
    path('LogoutUser/', views.LogoutUser, name='LogoutUser'),
]
