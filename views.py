from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
import os
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import random
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt

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
    

def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    pets = Pet.objects.filter(user=user)
    return render(request, 'user/user_profile.html', {'user': user, 'pets': pets})
    

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

        
        pet = Pet(
            pet_name=pet_name,
            pet_description=pet_description,
            pet_age=pet_age,
            pet_price=pet_price,
            pet_breed=pet_breed,
            category=category,
            pet_type=pet_type,
            pet_image=pet_image,
            user=request.user, 
            address=selected_address  
        )
        pet.save()

        return redirect('pet_list')  

    return render(request, 'user/addpets.html', {
        'categories': categories,
        'pet_types': pet_types,
        'addresses': addresses  
    })

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


@login_required
def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    addresses = Address.objects.filter(user=request.user)
    booking = Booking.objects.filter(pet=pet, user=request.user).first()

    is_adopted = Booking.objects.filter(pet=pet).exists()

    return render(request, 'user/pet_detail.html', {
        'pet': pet,
        'addresses': addresses,
        'booking': booking,
        'is_adopted': is_adopted,  
    })

    
def view_pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    address = pet.address 

    return render(request, 'admin/view_pet_details.html', {'pet': pet, 'address': address})

def pet_list(request):
    categories = Category.objects.all()
    pets = Pet.objects.all()[::-1]
    return render(request, 'user/pet_list.html', {'pets': pets,'categories': categories})



def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if pet.user != request.user:  
        messages.warning(request, "You are not authorized to edit this pet.")
        return redirect('pet_list')  

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

        if pet_image:  
            pet.pet_image = pet_image
        pet.save()

        messages.success(request, "Pet updated successfully.")
        return redirect('pet_list')

    return render(request, 'user/edit_pet.html', {
        'pet': pet,
        'categories': categories,
        'pet_types': pet_types
    })


def delete_pet(request, id):
    pet = get_object_or_404(Pet, id=id)

    if pet.user != request.user:  
        messages.warning(request, "You are not authorized to delete this pet.")
        return redirect('pet_list')  

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

        # Validate mobile number and pincode
        if len(mobile_no) != 10 or not mobile_no.isdigit():
            messages.warning(request, "Please enter a valid 10-digit mobile number.")
            return redirect('add_address')
        
        if len(str(pincode)) != 6 or not str(pincode).isdigit():
            messages.warning(request, "Please enter a valid 6-digit pincode.")
            return redirect('add_address')

        # Create the address
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
        return redirect('add_address')  # Redirect to the address list or another page

    return render(request, 'user/add_address.html')


@login_required
def view_address(request):
    categories = Category.objects.all()
    addresses = Address.objects.filter(user=request.user)  
    return render(request, 'user/view_address.html', {'addresses': addresses,'categories': categories})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('view_address')

    return render(request, 'user/address_delete.html', {'address': address})


def category_list(request):
    categories = Category.objects.all() 
    return render(request, 'user/cat_list.html', {'categories': categories})



def pets_by_category(request, category_id ):
    categories = Category.objects.all()
    pets = Pet.objects.filter(category_id=category_id) 
    category = Category.objects.get(id=category_id)  
    return render(request, 'user/pets_cat.html', {'pets': pets, 'category': category,'categories': categories})

@login_required
def view_bookings(request):
    # Fetch bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user)

    return render(request, 'user/view_bookings.html', {
        'bookings': bookings,
    })

# @login_required
# def book_pet(request, pet_id):
#     pet = get_object_or_404(Pet, id=pet_id)
#     addresses = Address.objects.filter(user=request.user)

#     # Check if the user has any saved addresses
#     if not addresses.exists():
#         messages.warning(request, "You need to add an address before booking a pet.")
#         return redirect('add_address')

#     if request.method == 'POST':
#         address_id = request.POST.get('address')
#         address = get_object_or_404(Address, id=address_id, user=request.user)

#         if pet.category.name.lower() == 'free':
#             # Create a booking for free adoption
#             booking = Booking(
#                 pet=pet,
#                 user=request.user,
#                 address=address,
#                 amount_paid=0,  # No payment for free adoption
#             )
#             booking.save()
#             messages.success(request, f"You have successfully booked {pet.pet_name} for free!")
#             return redirect('view_bookings')

#         else:
#             # Handle paid adoption
#             amount = pet.pet_price * 0.20  # Calculate 20% of the pet price
#             client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#             try:
#                 # Create a Razorpay order
#                 razorpay_order = client.order.create(
#                     {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
#                 )
#                 order_id = razorpay_order['id']
#                 order = Order.objects.create(
#                     user=request.user,
#                     amount=amount,
#                     provider_order_id=order_id,
#                     pet=pet,
#                     status=PaymentStatus.PENDING  # Set initial status to pending
#                 )

#                 return render(
#                     request,
#                     "user/payment.html",
#                     {
#                         "callback_url": "http://127.0.0.1:8000/callback",
#                         "razorpay_key": settings.RAZORPAY_KEY_ID,
#                         "order": order,
#                     },
#                 )
#             except Exception as e:
#                 messages.error(request, "There was an error processing your payment. Please try again.")
#                 return redirect('pet_list')

#     return render(request, 'user/book_pet.html', {'pet': pet, 'addresses': addresses})
@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            return client.utility.verify_payment_signature(response_data)
        except Exception:
            return False

    if request.method == 'POST':
        if "razorpay_signature" in request.POST:
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")
            
            try:
                # Retrieve the order from the database
                order = Order.objects.get(provider_order_id=provider_order_id)
                order.payment_id = payment_id
                order.signature_id = signature_id
                
                # Verify the payment signature
                if verify_signature(request.POST):
                    order.status = PaymentStatus.SUCCESS
                    order.save()  # Save the order status
                    # Create a booking for the paid adoption
                    booking = Booking(
                        pet=order.pet,
                        user=order.user,
                        address=order.user.address_set.first(),  # Assuming the first address is used
                        amount_paid=order.amount,
                    )
                    booking.save()  # Save the booking
                    messages.success(request, "Payment successful! Your pet has been booked.")
                else:
                    order.status = PaymentStatus.FAILURE
                    order.save()  # Save the order status
                    messages.error(request, "Payment verification failed.")
                
                return render(request, "callback.html", context={"status": order.status})

            except Order.DoesNotExist:
                messages.error(request, "Order not found.")
                return render(request, "callback.html", context={"status": "Order not found."})
            except Exception as e:
                messages.error(request, "An error occurred while processing your payment.")
                return render(request, "callback.html", context={"status": "An error occurred."})

        else:
            messages.error(request, "Invalid request. Signature not found.")
            return render(request, "callback.html", context={"status": "Invalid request."})

    else:
        messages.error(request, "Invalid request method.")
        return render(request, "callback.html", context={"status": "Invalid request method."})
    
    
# @login_required
# def confirm_payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)

#     return render(request, 'user/confirm_payment.html', {
#         'booking': booking,
#     })
    
# @login_required
# def process_payment(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)

#     if booking.amount_paid > 0:  # Only process payment if there is an amount
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         try:
#             # Create a Razorpay order
#             razorpay_order = client.order.create(
#                 {"amount": int(booking.amount_paid * 100), "currency": "INR", "payment_capture": "1"}
#             )
#             order_id = razorpay_order['id']
#             # Update the order in the database
#             order = Order.objects.create(
#                 user=request.user,
#                 amount=booking.amount_paid,
#                 provider_order_id=order_id,
#                 pet=booking.pet,
#                 status=PaymentStatus.PENDING  # Set initial status to pending
#             )

#             return render(
#                 request,
#                 "user/payment.html",
#                 {
#                     "callback_url": "http://127.0.0.1:8000/callback",
#                     "razorpay_key": settings.RAZORPAY_KEY_ID,
#                     "order": order,
#                 },
#             )
#         except Exception as e:
#             messages.error(request, "There was an error processing your payment. Please try again.")
#             return redirect('pet_list')

#     else:
#         messages.error(request, "No payment required for this booking.")
#         return redirect('view_bookings')    

@login_required
def book_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    addresses = Address.objects.filter(user=request.user)

    # Check if the user has any saved addresses
    if not addresses.exists():
        messages.warning(request, "You need to add an address before booking a pet.")
        return redirect('add_address')

    if request.method == 'POST':
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create a booking object
        booking = Booking(
            pet=pet,
            user=request.user,
            address=address,
            amount_paid=0,  # Initialize amount_paid to 0
        )
        booking.save()

        # Redirect to confirmation page
        return redirect('confirm_payment', booking_id=booking.id)

    return render(request, 'user/book_pet.html', {'pet': pet, 'addresses': addresses})

from django.shortcuts import get_object_or_404

@login_required
def confirm_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Calculate the amount for paid adoption
    if booking.pet.category.name.lower() != 'free':
        booking.amount_paid = booking.pet.pet_price * 0.20  # Calculate 20% of the pet price
    else:
        booking.amount_paid = 0  # No payment for free adoption

    return render(request, 'user/confirm_payment.html', {
        'booking': booking,
    })
    
    
@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.amount_paid > 0:  # Only process payment if there is an amount
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            # Create a Razorpay order
            razorpay_order = client.order.create(
                {"amount": int(booking.amount_paid * 100), "currency": "INR", "payment_capture": "1"}
            )
            order_id = razorpay_order['id']
            # Update the order in the database
            order = Order.objects.create(
                user=request.user,
                amount=booking.amount_paid,
                provider_order_id=order_id,
                pet=booking.pet,
                status=PaymentStatus.PENDING  # Set initial status to pending
            )

            return render(
                request,
                "user/payment.html",
                {
                    "callback_url": "http://127.0.0.1:8000/callback",
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "order": order,
                },
            )
        except Exception as e:
            messages.error(request, "There was an error processing your payment. Please try again.")
            return redirect('view_bookings')

    else:
        messages.success(request, "Your booking has been confirmed for free adoption!")
        return redirect('view_bookings')    