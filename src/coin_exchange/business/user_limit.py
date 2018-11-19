from coin_exchange.models import UserLimit
from coin_user.constants import VERIFICATION_LEVEL
from common.business import get_now


def reset_user_limit():
    UserLimit.objects.all().update(usage=0, updated_at=get_now())


def update_limit_by_level(level: str):
    assert(level in VERIFICATION_LEVEL)
