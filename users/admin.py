from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AppUser
from .forms import UserCreationForm, UserChangeForm

# Register your models here.

class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('uuid', 'is_staff', 'is_active',)
    list_filter = ('uuid', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('uuid',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uuid', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('uuid',)
    ordering = ('uuid',)


admin.site.register(User, UserAdmin)

admin.site.register(AppUser)