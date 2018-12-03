from coin_exchange.constants import CONFIG_USER_LIMIT
from coin_exchange.models import UserLimit
from coin_system.business import get_config
from coin_user.models import ExchangeUser
from common.business import get_now, RateManagement


def reset_user_limit():
    UserLimit.objects.all().update(usage=0, updated_at=get_now())


def update_limit_by_level(user: ExchangeUser):
    config = get_config(CONFIG_USER_LIMIT.format(user.currency, user.verification_level))
    UserLimit.objects.filter(user=user, fiat_currency=user.currency).update(limit=config.value)


def update_currency(user: ExchangeUser, currency: str):
    # We can do this because only 1 currency right now
    user_limit = UserLimit.objects.filter(user=user).first()
    if user_limit:
        if user_limit.currency != currency:
            old_currency = user_limit.currency
            user_limit.currency = currency
            user_limit.usage = RateManagement.convert_currency(user_limit.usage, old_currency, currency)
            user_limit.limit = RateManagement.convert_currency(user_limit.limit, old_currency, currency)
            user_limit.save()
