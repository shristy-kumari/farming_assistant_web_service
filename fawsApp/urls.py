from os import name
from django.urls import path
from .views import *


urlpatterns = [
    path('',index, name='index'  ),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    path('saved_page/', saved_page, name='saved_page'),
    path('shop_page/', shop_page, name='shop_page'),
    path('order_page/', order_page, name='order_page'),
    path('checkout_page/', checkout_page, name='checkout_page'),
    path('signout/', signout, name='signout'),
   
    
    

    # Register Page
    path('profile_page/', profile_page, name='profile_page'),  
    path('upload_profile/', upload_profile_pic, name='upload_profile'),
    path('profile_update/', profile_update, name='profile_update'),
    path('products/', products, name='products'),
    path('delete_product/<int:pk>/' , delete_product, name='delete_product'),
    path('add_to_cart/<int:pk>/' , add_to_cart, name='add_to_cart'),
    path('delete_cart/<int:pk>/' , delete_cart, name='delete_cart'),
    path('update_cart/<int:pk>/' , update_cart, name='update_cart'),
    path('change_password/', change_password, name='change_password'),
    path('register_page/', register_page, name='register_page'),
    path('register/', register, name='register'),

   
   # LOGIN PAGE AND FUNCTIONALITY
    path('login_page/', login_page, name='login_page'),
    path('login/', login, name='login'),

    # FORGOT PASSWORD PAGE AND FUNCTIONALITY
    path('forgot_pass_page/', forgot_pass_page, name='forgot_pass_page'),
    path('forgot_pass/', forgot_pass, name='forgot_pass'),

   
    # SEND OTP, OTP PAGE, VERIFIY OTP AND FUNCTIOALITY
    path('otp_page/', otp_page, name='otp_page'), 
    #path('verify_otp/', verify_otp, name='verify_otp'),
    path('verify_otp/<str:verify_for>/',verify_otp, name='otp_verify'),


    # PAYTM Payment 
    path('pay/', initiate_payment, name='pay'),
    path('callback/', callback, name='callback'),
]

