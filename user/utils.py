import random
import string
from django.utils.crypto import get_random_string
import jwt
from user.tasks import send_otp
from threading import Lock
import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)
lock = Lock()

REVOKED_TOKENS_SET = "revoked_tokens"
OTP_CACHE_TIMEOUT = getattr(settings, "OTP_CACHE_TIMEOUT", 300)
EMAIL_SENT_CACHE_TIMEOUT = getattr(settings, "EMAIL_SENT_CACHE_TIMEOUT", 300)
OTP_RETRY_WINDOW = getattr(settings, "OTP_RETRY_WINDOW", 60)  # In seconds
TOKEN_EXPIRATION_TIME = getattr(settings, "TOKEN_EXPIRATION_TIME", 60 * 60 * 24 * 7)
TOKEN_CACHE_PREFIX = "user_token"
TOKEN_CACHE_TIMEOUT = getattr(settings, "TOKEN_CACHE_TIMEOUT", 60 * 60 * 24)  # 1 day
HASH_ALGORITHM = getattr(settings, "HASH_ALGORITHM", "HS256")


def generate_otp():
    return get_random_string(6, string.digits)


def generate_profile_id():
    """Generate a string like 'asac2323'."""
    letters = random.choices(string.ascii_lowercase, k=4)
    digits = random.choices(string.digits, k=4)
    return "".join(letters + digits)


def generate_password():
    return get_random_string(10, string.ascii_letters + string.digits)


def generate_and_send_otp(email, force_new=False):
    email_cache_key = f"{email}_otp"
    email_sent_cache_key = f"email_sent_at_{email}"

    lock.acquire()
    try:
        otp = cache.get(email_cache_key)
        if otp and not force_new:
            email_sent_at = cache.get(email_sent_cache_key)
            if email_sent_at and timezone.now() - email_sent_at < datetime.timedelta(
                seconds=OTP_RETRY_WINDOW
            ):
                return

        otp = generate_otp()

        cache.set(email_cache_key, otp, timeout=OTP_CACHE_TIMEOUT)
        cache.set(
            email_sent_cache_key, timezone.now(), timeout=EMAIL_SENT_CACHE_TIMEOUT
        )

        is_sent = send_otp.delay(email=email, otp=otp)

        if not is_sent:
            logger.error(f"Error sending OTP to {email}")
            return False

        return True

    except Exception as e:
        logger.error(f"Error generating and sending OTP: {e}")
        return False

    finally:
        lock.release()


def generate_token(user, revoke_existing=False):
    cache_key = f"{TOKEN_CACHE_PREFIX}_{user.email}"
    token = cache.get(cache_key)

    if token and not revoke_existing:
        return token

    try:
        payload = get_token_payload(user)
        token = encode_token(payload)
        cache.set(cache_key, token, timeout=TOKEN_CACHE_TIMEOUT)

        if revoke_existing:
            revoke_token(user)

    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None

    return token


def revoke_token(token):
    """Revoke a token by adding it to the revoked tokens set."""
    revoked_tokens = cache.get(REVOKED_TOKENS_SET, set())
    revoked_tokens.add(token)
    cache.set(REVOKED_TOKENS_SET, revoked_tokens, None)


def is_token_revoked(token):
    """Check if a token has been revoked."""
    revoked_tokens = cache.get(REVOKED_TOKENS_SET, set())
    return token in revoked_tokens


def decode_token(token):
    """Decode a token and raise an exception if it's revoked."""
    secret_key = settings.SECRET_KEY
    algorithm = settings.HASH_ALGORITHM

    if is_token_revoked(token):
        raise jwt.exceptions.InvalidTokenError("Token has been revoked.")

    return jwt.decode(token, secret_key, algorithms=[algorithm])


def get_token_payload(user):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(
        hours=TOKEN_EXPIRATION_TIME
    )

    payload = {
        "user_id": str(user.profile_id),
        "expires_at": str(expiration_time),
    }

    return payload


def encode_token(payload):
    secret_key = settings.SECRET_KEY
    algorithm = settings.HASH_ALGORITHM

    return jwt.encode(payload, secret_key, algorithm=algorithm)


def validate_token(token):
    try:
        decode_token(token)
        return True
    except jwt.exceptions.DecodeError:
        return False

    except jwt.exceptions.InvalidTokenError:
        return False


def get_user_from_token(token):
    from user.models import CustomUser

    try:
        payload = decode_token(token)
        return CustomUser.objects.get(profile_id=payload["user_id"])
    except jwt.exceptions.DecodeError:
        return None
