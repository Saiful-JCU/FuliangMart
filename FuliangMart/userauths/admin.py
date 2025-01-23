from django.contrib import admin
from userauths.models import User, ContactUs, Profile

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'bio']

class ProfileAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'full_name', 'image', 'phone', 'bio', 'verified']

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'message']

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactUs, ContactUsAdmin)