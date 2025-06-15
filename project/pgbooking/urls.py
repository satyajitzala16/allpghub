from django.urls import path,include
from .views import index,register,about_us,contact_us,catpro,submit_feedback,get_pg_images, delete_pg_image,allroom,booking,admin,forget,prodetails,city,pgarea,register_owner,loginsel,owner,owner_login,admin_login,add_pg,addroom,profile,update,view_pg_data,view_data,view_room_data,view_booking_data,add_food,success_page,view_weekly_meal_plan,forgot_password,pg_list_view,upload_pg_images
from .import views
from django.contrib.auth import views as auth_views



urlpatterns = [
  path('',views.index,name='index'),# index page
  path('reg/',views.register,name='register'),# user register page
  path('verify_otp/', views.verify_otp, name='verify_otp'),
  path('login/',views.login,name='login'),# user login page
  path('logout/',views.logout,name='logout'),# user and owner logout
  path('allroom/',views.allroom,name='allroom'),# all room show
  path('about/',views.about_us,name='about_us'),# pg service
  path('cont/',views.contact_us,name='contact_us'),# contact deatils
  path('catpro/<str:pgname>/',views.catpro,name='catpro'), # user select pg than pg type of room show 
  path('book/<int:id>',views.booking,name='book'),# user click book Now and book the pg
  # path('payment/success/', payment_success, name='payment_success'),
  # path('payment-success/', views.payment_success, name='payment-success'),
  path('submit_feedback/', submit_feedback, name='submit_feedback'),
  
  path('add/',views.admin,name='admin'),
  path('for/',views.forget,name='forget'),# user and owner forget password
  path('prodetails/<int:id>',views.prodetails,name='prodetails'), # user click pg room and show deatils
  path('gender/<str:gender>/', views.gender, name='gender'),
  path('city/<str:gender>/', views.city, name='city'),# select city all pg show 
  path('city/pgarea/<int:pg_id>/', views.pgarea, name='pgarea'), # select pg deatils 
  path('owner/',views.register_owner,name='register_owner'), # owner register
  path('approve_owner/<int:owner_id>/', views.approve_owner, name='approve_owner'),
  path('loginsel/',views.loginsel,name='loginsel'),
  path('owners/',views.owner,name='owner'),# owner add pg and room
  path('adminlogin/',views.admin_login,name='adminlogin'),
  path('ownerlogin/',views.owner_login,name='ownerlogin'), # owner login
  path('addpg/',views.add_pg,name='addpg'), # owner add pg
  path('addroom/',views.addroom,name='addroom'), # owner add room
  path('get_pg_details/', views.get_pg_details, name='get_pg_details'),
  path('profile/',views.profile,name='profile'), # user profile
  path('update/',views.update,name='update'), # user profile update
  path('checkout/<int:user_id>/', views.checkout, name='checkout'),
  # path('payment_success/<int:user_profile_id>/', views.payment_success, name='payment_success'),
  path('booking-confirmation/', views.booking_confirmation, name='booking_confirmation'),
  path('error/', views.error_page, name='error_page'),
  path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
  path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
  path('viewdata/',view_data,name='view_data'),
  path('viewpgdata/', view_pg_data, name='view_pg_data'),
  path('get_pg_images/', get_pg_images, name='get_pg_images'),
  path('delete_pg_image/', delete_pg_image, name='delete_pg_image'),
  path('room/view/', views.view_room_data, name='view_room_data'),
  path('viewbookingdata/', views.view_booking_data, name='viewbookingdata'),
  path('addfood/', views.add_food, name='add_food'),
  path('success/', success_page, name='success_page'),  # Success page URL
  path('meal-plan/<int:pg_id>/', views.view_weekly_meal_plan, name='view_weekly_meal_plan'),
  path('no-data-found/', views.no_data_found, name='no_data_found'),  # URL for the no-data-found page
  path('view-food-data/', views.view_food_data, name='view_food_data'),
  

  # 
  # path('forgotpassword', views.forgot_password, name='forgotpwd'),
  # path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
  path('forgot-password/', views.forgot_password, name='forgot_password'),
  path('otp-verify/', views.otp_verify, name='otp_verify'),
  path('change-password/', views.change_password, name='change_password'),

  path('owner/forgot-password/', views.owner_forgot_password, name='owner_forgot_password'),
  path('owner/otp-verify/', views.owner_otp_verify, name='owner_otp_verify'),
  path('owner/change-password/', views.owner_change_password, name='owner_change_password'),
  path('pg-list/', pg_list_view, name='pg_list'),  # Add this line
  # path('payment-success/', views.payment_success, name='payment-success'),
  path('like_pg/<int:pg_id>/', views.like_pg, name='like_pg'),
  path('comment_pg/<int:pg_id>/', views.comment_pg, name='comment_pg'),
  path('rate_room/<int:room_id>/', views.rate_room, name='rate_room'),
  path('upload_pg_images/', views.upload_pg_images, name='upload_pg_images'),
  path('upload_success/', views.upload_success, name='upload_success'),
  # path('find_nearby_pgs/', views.find_nearby_pgs, name='find_nearby_pgs'),
  
]  