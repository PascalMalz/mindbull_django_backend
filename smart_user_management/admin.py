from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfileInformation, Follow,RegistrationToken

#This is only the info how a user should be displayed in django admin if it is customuser or standard user
class CustomUserAdmin(UserAdmin):
    list_display = ('id','username', 'email', 'first_name', 'last_name', 'is_active','is_staff', 'profile_picture_url')

class ProfileInformationAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'profile_picture')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower_id', 'following_id', 'created_at', 'status')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProfileInformation, ProfileInformationAdmin)
admin.site.register(Follow, FollowAdmin)


from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin as DefaultOutstandingTokenAdmin

# Unregister the original admin model registration
admin.site.unregister(OutstandingToken)

@admin.register(OutstandingToken)
class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'token','jti', 'expires_at')
    search_fields = ('user__username',)

    def jti_short(self, obj):
        # Assuming 'jti' is a field you've added or can extract
        return str(obj.jti)
    jti_short.short_description = 'JTI'



""" #Dont unregister users when you defined a custom user
#admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin) 

# Register your custom user model with the admin site
admin.site.register(CustomUser, UserAdmin) """