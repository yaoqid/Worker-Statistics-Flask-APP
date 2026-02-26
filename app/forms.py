from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    IntegerField,
    PasswordField,
    SubmitField
)
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime

# Code is helped by ChatGPT
# Custom validator: Year must not be in the future.
def validate_not_future(form, field):
    current_year = datetime.utcnow().year
    if field.data > current_year:
        raise ValidationError("Year cannot be in the future.")


# Class for the form to add a new worker category
# This form is used to add a new worker category to the database
class DisabilityStatusForm(FlaskForm):
    disability_status = SelectField(
        'Disability Status',
        choices=[
            ('Equality Act Disabled', 'Equality Act Disabled'),
            ('Not Equality Act Disabled', 'Not Equality Act Disabled')
        ],
        validators=[DataRequired(message="Please select Disability Status")]
    )
    weighted_count = IntegerField(
        'Weighted Count',
        validators=[
            DataRequired(message="Please enter a positive integer"),
            NumberRange(min=1, message="Must be a positive integer")
        ]
    )
    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the year"),
            validate_not_future
        ]
    )
    category_name = SelectField(
        'Category Name',
        choices=[('Night', 'Night'), ('Day', 'Day')],
        validators=[DataRequired(message="Please select Category Name")]
    )
    submit = SubmitField('Submit')


# Class for the Age Band form
# This form is used to add a year to the database
class AgeBandForm(FlaskForm):
    age_band = SelectField(
        'Age Band',
        choices=[
            ('16-21', '16-21'),
            ('21-26', '21-26'),
            ('26-31', '26-31'),
            ('31-36', '31-36'),
            ('36-41', '36-41'),
            ('41-46', '41-46'),
            ('46-51', '46-51'),
            ('51-56', '51-56'),
            ('56-61', '56-61'),
            ('61-66', '61-66')
        ],
        validators=[DataRequired(message="Please select Age Band")]
    )
    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the year"),
            validate_not_future
        ]
    )
    category_name = SelectField(
        'Category Name',
        choices=[('Night', 'Night'), ('Day', 'Day')],
        validators=[DataRequired(message="Please select Category Name")]
    )
    submit = SubmitField('Submit')


# Class for the Skill Level form
# This form is used to add a year to the database
class SkillLevelForm(FlaskForm):
    skill_level = SelectField(
        'Skill Level',
        choices=[
            ('Level 1', 'Level 1'),
            ('Level 2', 'Level 2'),
            ('Level 3', 'Level 3'),
            ('Level 4', 'Level 4')
        ],
        validators=[DataRequired(message="Please select Skill Level")]
    )
    weighted_count = IntegerField(
        'Weighted Count',
        validators=[
            DataRequired(message="Please enter a positive integer"),
            NumberRange(min=1, message="Must be a positive integer")
        ]
    )
    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the year"),
            validate_not_future
        ]
    )
    category_name = SelectField(
        'Category Name',
        choices=[('Night', 'Night'), ('Day', 'Day')],
        validators=[DataRequired(message="Please select Category Name")]
    )
    submit = SubmitField('Submit')


# Class for sex form
# This form is used to add a year to the database
class SexForm(FlaskForm):
    sex = SelectField(
        'Sex',
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female')
        ],
        validators=[DataRequired(message="Please select Sex")]
    )
    weighted_count = IntegerField(
        'Weighted Count',
        validators=[
            DataRequired(message="Please enter a positive integer"),
            NumberRange(min=1, message="Must be a positive integer")
        ]
    )
    year = IntegerField(
        'Year',
        validators=[
            DataRequired(message="Please enter the year"),
            validate_not_future
        ]
    )
    category_name = SelectField(
        'Category Name',
        choices=[('Night', 'Night'), ('Day', 'Day')],
        validators=[DataRequired(message="Please select Category Name")]
    )
    submit = SubmitField('Submit')


# Class for the login form
# This form is used to log in to the admin dashboard
class AdminLoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(message="Please enter a username")]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Please enter a password")]
    )
    submit = SubmitField('Login')
