from django.contrib import admin
from . models import*
# Register your models here.
admin.site.register(Category)
admin.site.register(PetType)
admin.site.register(Pet)
admin.site.register(Address)
admin.site.register(Booking)
admin.site.register(Profile)
admin.site.register(Otp)