from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, QueryLog, LiveClassBooking, MathGameResult

# Inline profile editing under User
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend default User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Unregister original User admin and register the extended one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Profile)
admin.site.register(QueryLog)
admin.site.register(LiveClassBooking)
admin.site.register(MathGameResult)
