from django .urls import path 
from . import views 


urlpatterns=[

    path('',views.pet_login),
    path('logout',views.pet_logout),

#--------------------admin----------------------------

    path('admin_home',views.admin_home),
    path('view-pets', views.view_all_pets, name='view_all_pets'),
    path('view-pet-detail/<int:pet_id>', views.view_pet_detail, name='view_pet_detail'),
#--------------------user-----------------------------

    path('register',views.register),
    path('otp',views.otp_confirmation),
    path('user_home',views.user_home),
    path('add-pet', views.add_pet, name='add_pet'),
    path('add-category', views.add_category, name='add_category'),
    path('add-pet-type', views.add_pet_type, name='add_pet_type'),
    path('pet-list', views.pet_list, name='pet_list'),
    path('pet-detail/<int:pet_id>', views.pet_detail, name='pet_detail'),
    path('pet/edit/<int:pet_id>', views.edit_pet, name='edit_pet'),
    path('pet/<int:id>/delete', views.delete_pet, name='delete_pet'),  
    path('add_address', views.add_address, name='add_address'),
    path('view_address', views.view_address, name='view_address'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),
    path('categories', views.category_list, name='category_list'),
    path('pets/category/<int:category_id>', views.pets_by_category, name='pets_by_category'),
    path('user/<int:user_id>/profile/', views.user_profile, name='user_profile'),





]    