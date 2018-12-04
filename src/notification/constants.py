from model_utils import Choices

EMAIL_PURPOSE = Choices(
    ('email_verification', 'Email verification'),
    ('forgot_password', 'Forgot password'),
    ('successful_email_verification', 'Successful email verification'),
    ('successful_phone_verification', 'Successful phone verification'),
    ('successful_id_verification', 'Successful ID verification'),
    ('failed_id_verification', 'Failed ID verification'),
    ('successful_selfie_verification', 'Successful selfie verification'),
    ('failed_selfie_verification', 'Failed selfie verification'),
    ('gift_promotion', 'Gift promotion'),
    ('coin_price', 'Coin price'),
    ('successful_buying', 'Successful buying'),
    ('successful_selling', 'Successful selling'),
)

SMS_PURPOSE = Choices(
    ('phone_verification', 'Phone verification'),
)

NOTIFICATION_TARGET = Choices(
    ('user', 'User'),
    ('system', 'System'),
)

NOTIFICATION_METHOD = Choices(
    ('email', 'Email'),
    ('slack', 'Slack'),
    ('sms', 'SMS'),
    ('call', 'Call'),
)

NOTIFICATION_GROUP = Choices(
    ('verification', 'Verification'),
    ('order', 'Order'),
)

STATIC_PAGE = Choices(
    ('about_us', 'About Us'),
    ('privacy', 'Privacy'),
    ('agreement', 'Agreement'),
    ('promotion_programs', 'Promotion Programs'),
    ('how_it_works', 'How It Works'),
)
