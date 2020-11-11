from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AppUser, ManagerUser, PromoterUser
from .forms import UserCreationForm, UserChangeForm

# Register your models here.

class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('id', 'is_staff', 'is_active',)
    list_filter = ('id', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('id',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('id',)
    ordering = ('id',)


admin.site.register(User, UserAdmin)

admin.site.register(AppUser)
admin.site.register(ManagerUser)
admin.site.register(PromoterUser)
