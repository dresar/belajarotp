from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),  # Login sebagai halaman utama
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/<str:purpose>/', views.verify_otp_view, name='verify_otp'),
    path('verify-otp-token/<str:token>/', views.verify_otp_token_view, name='verify_otp_token'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('reset-password-token/<str:token>/', views.reset_password_token_view, name='reset_password_token'),
    path('daftar-ppt/', views.ppt_registration_view, name='ppt_registration'),
    path('daftar-ppt/success/', views.ppt_registration_success_view, name='ppt_registration_success'),
    path('kirim-email-massal/', views.send_mass_email_view, name='send_mass_email'),
]

