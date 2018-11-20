from coin_exchange.models import UserLimit
from coin_system.business import get_config
from coin_system.constants import SYSTEM_CONFIG
from coin_user.models import ExchangeUser
from common.business import get_now


def reset_user_limit():
    UserLimit.objects.all().update(usage=0, updated_at=get_now())


def update_limit_by_level(user: ExchangeUser):
    config = get_config('{}_{}_{}'.format(user.currency.lower(), SYSTEM_CONFIG.user_limit, user.verification_level))
    UserLimit.objects.filter(user=user, fiat_currency=user.currency).update(limit=config.value)
