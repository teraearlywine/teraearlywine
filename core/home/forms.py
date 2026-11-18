from flask_wtf import FlaskForm
from wtforms import HiddenField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

UNSCOPED_ENGAGEMENT = 'Help me scope it'
WAREHOUSE_DIAGNOSTIC_ENGAGEMENT = 'Warehouse cost diagnostic'
PROJECT_DELIVERY_ENGAGEMENT = 'Value / Risk Diagnostic'
DATA_REPORTING_ENGAGEMENT = 'Data Foundation Blueprint'
AI_AUTOMATION_ENGAGEMENT = 'Production AI Lighthouse'


def _strip(value):
    """Normalize user-entered text before validation and delivery."""
    return value.strip() if isinstance(value, str) else value


class ContactForm(FlaskForm):
    name = StringField(
        'Name',
        filters=[_strip],
        validators=[
            DataRequired(message='Enter your name.'),
            Length(max=100, message='Use 100 characters or fewer.'),
        ],
    )
    email = StringField(
        'Work email',
        filters=[_strip],
        validators=[
            DataRequired(message='Enter your email address.'),
            Length(max=254, message='Use 254 characters or fewer.'),
            Email(
                check_deliverability=False,
                message='Enter a valid email address.',
            ),
        ],
    )
    engagement_type = RadioField(
        'What would you like help with?',
        choices=[
            (PROJECT_DELIVERY_ENGAGEMENT, 'Data and AI project delivery'),
            (DATA_REPORTING_ENGAGEMENT, 'Data and reporting'),
            (AI_AUTOMATION_ENGAGEMENT, 'AI and workflow automation'),
            (WAREHOUSE_DIAGNOSTIC_ENGAGEMENT, WAREHOUSE_DIAGNOSTIC_ENGAGEMENT),
            (UNSCOPED_ENGAGEMENT, UNSCOPED_ENGAGEMENT),
        ],
        validators=[
            DataRequired(message='Select an engagement type.'),
        ],
    )
    message = TextAreaField(
        'Message',
        filters=[_strip],
        validators=[
            DataRequired(message='Enter a message.'),
            Length(
                min=10,
                max=5000,
                message='Use between 10 and 5,000 characters.',
            ),
        ],
    )
    website = StringField(
        'Website',
        validators=[
            Optional(),
            Length(max=0, message='Leave this field empty.'),
        ],
    )
    submission_id = HiddenField(validators=[DataRequired()])
