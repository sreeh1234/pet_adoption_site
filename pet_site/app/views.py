from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.

def pet_login(req):
    if 'shop' in req.session:
        return redirect(admin_home)
    if 'user' in req.session:
        return redirect(user_home)
    if req.method=='POST':
        uname=req.POST['uname']
        password=req.POST['password']
        shop=authenticate(username=uname,password=password)
        if shop:
            login(req,shop)
            if shop.is_superuser:
                
                req.session['shop']=uname       
                return redirect(admin_home)
            else:
                req.session['user']=uname
                return redirect(user_home)
        else:
            messages.warning(req,'invalid username or password')
            return redirect(pet_login)
    else:
        return render(req,'login.html')

def pet_logout(req):
    logout(req)
    req.session.flush()        
    return redirect(pet_login)


#-----------------------admin-----------------------


def admin_home(req):
    if 'shop' in req.session:
        # products=details.objects.all()
        return render(req,'admin/home.html')
    else:
        return redirect(pet_login)
    
def view_all_pets(req):
    if 'shop' in req.session:
        pets = Pet.objects.all()[::-1] 
        return render(req, 'admin/view_pets.html', {'pets': pets})
    else:
        return redirect(pet_login)     




#-----------------------user-----------------------

def register(req):
    if req.method == 'POST':
        uname = req.POST['uname']
        email = req.POST['email']
        pswd = req.POST['pswd']
        try:
            data = User.objects.create_user(first_name=uname, email=email, username=email, password=pswd)
            data.save()
            otp = ""
            for i in range(6):
                otp += str(random.randint(0, 9))
            msg = f'Your registration is completed otp: {otp}'
            otp = Otp.objects.create(user=data, otp=otp)
            otp.save()
            send_mail('Registration', msg, settings.EMAIL_HOST_USER, [email])
            messages.success(req, "Registration successful. Please check your email for OTP.")
            return redirect(otp_confirmation)
        except:
            messages.warning(req, 'Email already exists')
            return redirect(register)
    else:
        return render(req, 'user/register.html')

    
def otp_confirmation(req):
    if req.method == 'POST':
        uname = req.POST.get('uname')
        user_otp = req.POST.get('otp')
        try:
            user = User.objects.get(username=uname)
            generated_otp = Otp.objects.get(user=user)
    
            if generated_otp.otp == user_otp:
                generated_otp.delete()
                return redirect(pet_login)
            else:
                messages.warning(req, 'Invalid OTP')
                return redirect(otp_confirmation)
        except User.DoesNotExist:
            messages.warning(req, 'User does not exist')
            return redirect(otp_confirmation)
        except Otp.DoesNotExist:
            messages.warning(req, 'OTP not found or expired')
            return redirect(otp_confirmation)
    return render(req, 'user/otp.html')



def user_home(request):

    if 'user' in request.session:

        categories = Category.objects.all()  
        user = User.objects.get(username=request.session['user'])
        return render(request, 'user/home.html', {'categories': categories})

    else:

        return redirect(pet_login)
    


@login_required
def add_pet(request):
    categories = Category.objects.all()
    pet_types = PetType.objects.all()
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        pet_name = request.POST.get('pet_name')
        pet_description = request.POST.get('pet_description')
        pet_age = request.POST.get('pet_age')
        pet_price = request.POST.get('pet_price')
        pet_breed = request.POST.get('pet_breed')
        category_id = request.POST.get('category')
        pet_type_id = request.POST.get('pet_type')
        pet_image = request.FILES.get('pet_image')  

        category = Category.objects.get(id=category_id)
        pet_type = PetType.objects.get(id=pet_type_id)

        address_id = request.POST.get('address') 
        selected_address = Address.objects.get(id=address_id) if address_id else None

        # Make sure you're passing the correct fields to the Pet constructor
        pet = Pet(
            pet_name=pet_name,
            pet_description=pet_description,
            pet_age=pet_age,
            pet_price=pet_price,
            pet_breed=pet_breed,
            category=category,
            pet_type=pet_type,
            pet_image=pet_image,
            user=request.user,  # Assign logged-in user
            address=selected_address  # Address assigned based on user's selection
        )
        pet.save()

        return redirect('pet_list')  

    return render(request, 'user/addpets.html', {
        'categories': categories,
        'pet_types': pet_types,
        'addresses': addresses  
    })


def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    pets = Pet.objects.filter(user=user)
    return render(request, 'user/user_profile.html', {'user': user, 'pets': pets})

  






def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')
        category = Category(name=category_name)
        category.save()
        
        
        messages.success(request, 'Category added successfully!')
        return redirect('add_category')  

    return render(request, 'user/add_category.html')


def add_pet_type(request):
    if request.method == 'POST':
        pet_type_name = request.POST.get('name')
        
        pet_type = PetType(name=pet_type_name)
        pet_type.save()
        
        messages.success(request, 'Pet type added successfully!')
        return redirect('add_pet_type')  

    return render(request, 'user/add_pet_type.html')

def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    user = request.user
    address = pet.address 
    return render(request, 'user/pet_detail.html', {'pet': pet, 'address': address, 'user': user})

def view_pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    address = pet.address 

    return render(request, 'admin/view_pet_details.html', {'pet': pet, 'address': address})



def pet_list(request):
    pets = Pet.objects.all()[::-1]
    return render(request, 'user/pet_list.html', {'pets': pets})



# def edit_pet(request, pet_id):
#     pet = get_object_or_404(Pet, id=pet_id)  
#     categories = Category.objects.all()
#     pet_types = PetType.objects.all()

#     if request.method == 'POST':
#         pet_name = request.POST.get('pet_name')
#         pet_description = request.POST.get('pet_description')
#         pet_age = request.POST.get('pet_age')
#         pet_price = request.POST.get('pet_price')
#         pet_breed = request.POST.get('pet_breed')
#         category_id = request.POST.get('category')
#         pet_type_id = request.POST.get('pet_type')
#         pet_image = request.FILES.get('pet_image')

#         if not pet_name or not pet_description or not pet_age or not pet_price or not pet_breed:
#             messages.error(request, "All fields are required.")
#             return render(request, 'user/edit_pet.html', {
#                 'pet': pet,
#                 'categories': categories,
#                 'pet_types': pet_types
#             })

#         try:
#             pet_age = int(pet_age)
#             pet_price = int(pet_price)
#         except ValueError:
#             messages.error(request, "Age and price must be numbers.")
#             return render(request, 'user/edit_pet.html', {
#                 'pet': pet,
#                 'categories': categories,
#                 'pet_types': pet_types
#             })

#         try:
#             category = Category.objects.get(id=category_id)
#             pet_type = PetType.objects.get(id=pet_type_id)
#         except Category.DoesNotExist:
#             messages.error(request, "Invalid category.")
#             return render(request, 'user/edit_pet.html', {
#                 'pet': pet,
#                 'categories': categories,
#                 'pet_types': pet_types
#             })
#         except PetType.DoesNotExist:
#             messages.error(request, "Invalid pet type.")
#             return render(request, 'user/edit_pet.html', {
#                 'pet': pet,
#                 'categories': categories,
#                 'pet_types': pet_types
#             })

#         pet.pet_name = pet_name
#         pet.pet_description = pet_description
#         pet.pet_age = pet_age
#         pet.pet_price = pet_price
#         pet.pet_breed = pet_breed
#         pet.category = category
#         pet.pet_type = pet_type

#         if pet_image: 
#             pet.pet_image = pet_image
#         pet.save()

#         messages.success(request, "Pet updated successfully.")
#         return redirect('pet_list')  
    
#     return render(request, 'user/edit_pet.html', {
#         'pet': pet,
#         'categories': categories,
#         'pet_types': pet_types
#     })

def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if pet.user != request.user:  # Check if the pet belongs to the logged-in user
        messages.warning(request, "You are not authorized to edit this pet.")
        return redirect('pet_list')  # Redirect to the pet list page

    categories = Category.objects.all()
    pet_types = PetType.objects.all()

    if request.method == 'POST':
        pet_name = request.POST.get('pet_name')
        pet_description = request.POST.get('pet_description')
        pet_age = request.POST.get('pet_age')
        pet_price = request.POST.get('pet_price')
        pet_breed = request.POST.get('pet_breed')
        category_id = request.POST.get('category')
        pet_type_id = request.POST.get('pet_type')
        pet_image = request.FILES.get('pet_image')

        if not pet_name or not pet_description or not pet_age or not pet_price or not pet_breed:
            messages.error(request, "All fields are required.")
            return render(request, 'user/edit_pet.html', {
                'pet': pet,
                'categories': categories,
                'pet_types': pet_types
            })

        try:
            pet_age = int(pet_age)
            pet_price = int(pet_price)
        except ValueError:
            messages.error(request, "Age and price must be numbers.")
            return render(request, 'user/edit_pet.html', {
                'pet': pet,
                'categories': categories,
                'pet_types': pet_types
            })

        try:
            category = Category.objects.get(id=category_id)
            pet_type = PetType.objects.get(id=pet_type_id)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category.")
            return render(request, 'user/edit_pet.html', {
                'pet': pet,
                'categories': categories,
                'pet_types': pet_types
            })
        except PetType.DoesNotExist:
            messages.error(request, "Invalid pet type.")
            return render(request, 'user/edit_pet.html', {
                'pet': pet,
                'categories': categories,
                'pet_types': pet_types
            })

        pet.pet_name = pet_name
        pet.pet_description = pet_description
        pet.pet_age = pet_age
        pet.pet_price = pet_price
        pet.pet_breed = pet_breed
        pet.category = category
        pet.pet_type = pet_type

        if pet_image:  # Only update image if a new one is uploaded
            pet.pet_image = pet_image
        pet.save()

        messages.success(request, "Pet updated successfully.")
        return redirect('pet_list')

    return render(request, 'user/edit_pet.html', {
        'pet': pet,
        'categories': categories,
        'pet_types': pet_types
    })


# def delete_pet(request, id):
#     pet = get_object_or_404(Pet, id=id)

#     if request.method == 'POST':
#         pet.delete()
#         return redirect('pet_list')

#     return render(request, 'user/confirm_delete.html', {'pet': pet})
def delete_pet(request, id):
    pet = get_object_or_404(Pet, id=id)

    if pet.user != request.user:  # Check if the pet belongs to the logged-in user
        messages.warning(request, "You are not authorized to delete this pet.")
        return redirect('pet_list')  # Redirect to the pet list page

    if request.method == 'POST':
        pet.delete()
        messages.success(request, "Pet deleted successfully.")
        return redirect('pet_list')

    return render(request, 'user/confirm_delete.html', {'pet': pet})



@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        building_no = request.POST.get('building_no')
        street = request.POST.get('street')
        state = request.POST.get('state')
        district = request.POST.get('district')
        pincode = request.POST.get('pincode')
        mobile_no = request.POST.get('mobile_no')

        # Validate pincode and mobile number formats (basic validation)
        if len(mobile_no) != 10 or not mobile_no.isdigit():
            messages.warning(request, "Please enter a valid 10-digit mobile number.")
            return redirect('add_address')
        
        if len(str(pincode)) != 6 or not str(pincode).isdigit():
            messages.warning(request, "Please enter a valid 6-digit pincode.")
            return redirect('add_address')
        
        address = Address(
            user=request.user,
            name=name,
            building_no=building_no,
            street=street,
            state=state,
            district=district,
            pincode=pincode,
            mobile_no=mobile_no
        )
        address.save()
        messages.success(request, "Address added successfully!")
        return redirect(user_home)  

    return render(request, 'user/add_address.html')


@login_required
def view_address(request):
    addresses = Address.objects.filter(user=request.user)  
    return render(request, 'user/view_address.html', {'addresses': addresses})



# @login_required
# def delete_address(request, address_id):
#     address = get_object_or_404(Address, id=address_id, user=request.user) 

#     if request.method == 'POST':
#         address.delete()
#         messages.success(request, "Address deleted successfully.")
#         return redirect(user_home)  

#     return render(request, 'user/address_delete.html', {'address': address})
@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('view_address')

    return render(request, 'user/address_delete.html', {'address': address})


def category_list(request):
    categories = Category.objects.all()  # Retrieve all categories
    return render(request, 'user/cat_list.html', {'categories': categories})

def pets_by_category(request, category_id ):
    pets = Pet.objects.filter(category_id=category_id)  # Filter pets by category
    category = Category.objects.get(id=category_id)  # Get the category name 
    return render(request, 'user/pets_cat.html', {'pets': pets, 'category': category})