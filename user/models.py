from django.db import models
from user.common import UserCommonFields
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from user.managers import CustomUserManager


class CustomUser(UserCommonFields, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    maker = models.CharField(max_length=50, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email

    # Permission related methods
    class Meta(UserCommonFields.Meta):
        verbose_name = "User"
        verbose_name_plural = "Users"
        permissions = (
            ("view_user", "View user"),
            ("edit_user", "Edit user"),
            ("delete_user", "Delete user"),
            ("create_user", "Create user"),
            ("revoke_token", "Revoke token"),
            ("suspend_user", "Suspend user"),
        )
