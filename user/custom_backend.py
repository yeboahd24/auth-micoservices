from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


CustomUser = get_user_model()


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


class AuthenticateUser(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = kwargs.get(CustomUser.USERNAME_FIELD)
        try:
            user = get_or_none(CustomUser, email=email)
            if user and user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return AnonymousUser(None, None)
