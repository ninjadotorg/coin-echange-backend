from model_utils import Choices

VERIFICATION_LEVEL = Choices(
    ('level_0', 'Not Verified'),
    ('level_1', 'Level 1'),
    ('level_2', 'Level 2'),
    ('level_3', 'Level 3'),
    ('level_4', 'Level 4'),
)

VERIFICATION_STATUS = Choices(
    ('not_yet', 'Not Yet'),
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
)

ID_TYPE = Choices(
    ('passport', 'Passport'),
    ('driver_license', 'Driver License'),
    ('id_card', 'Government ID Card'),
)
