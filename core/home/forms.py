from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


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
        'Email',
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
