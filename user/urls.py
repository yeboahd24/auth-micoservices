from django.urls import path
from user.api_views.healthCheck import health_check
from user.api_views.signup import signup
from user.api_views.login import login_view
from user.api_views.token import verif_token, remove_token_view
from user.api_views.otp_verification import otp_verification_view
from user.api_views.otp_resend import resend_otp
from user.api_views.users import get_users
from user.api_views.suspend_user import suspend_user
from user.api_views.activate_user import activate_user

urlpatterns = [
    path("health-check/", health_check, name="health_check"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("verify-token/", verif_token, name="verif_token"),
    path("revoke-token/", remove_token_view, name="revoke_token"),
    path("otp-verification/", otp_verification_view, name="otp_verification"),
    path("otp-resend/", resend_otp, name="otp_resend"),
    path("users/", get_users, name="users"),
    path("suspend-user/", suspend_user, name="suspend_user"),
    path("activate-user/", activate_user, name="activate_user"),
]
