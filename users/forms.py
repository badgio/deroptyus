from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ()


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ()
