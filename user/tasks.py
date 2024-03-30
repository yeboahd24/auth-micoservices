from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from celery import shared_task
import os


@shared_task(routing_key="user")
def send_otp(email, otp):
    print("Sending OTP")
    subject = "Mesika Authentication OTP"
    message = f"Your OTP is {otp}"
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, sender_email, recipient_list)


@shared_task(routing_key="user")
def send_password_reset_email(user_id):
    from user.models import CustomUser

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return

    token = default_token_generator.make_token(user)
    reset_url = (
        f"{os.environ.get('FRONTEND_URL')}/reset-password/{user.profile_id}/{token}"
    )
    user.password_reset_token = token
    user.password_reset_token_created_at = timezone.now()
    user.save()
    message = f"Click the link below to reset your password: {reset_url}"

    send_mail(
        "Mesika Password Reset",
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=message,
    )


@shared_task(routing_key="user")
def send_user_credentials(email, password):
    link = os.environ.get("FRONTEND_URL")
    subject = "Mesika User Credentials"
    message = f"Your credentials are: Email: {email} Password: {password} Click the link below to login: {link}"
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, sender_email, recipient_list)
