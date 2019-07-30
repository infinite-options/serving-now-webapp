#  Prashant Marathay
#  Flask Tutorial Video 3  https://www.youtube.com/watch?v=UIJKdCIEXUQ
#  Most everything is available in wt forms
#  Could go into main application file but better to break out
#  Write python class that will automatically be converted into html form in the template (1:55)

from flask_wtf import FlaskForm # imports to
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TimeField, RadioField # imports these classes
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm): # create a Registration Form class.  Below are the form fields
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])  # StringField must identify Username as the label so form.username.label takes you to the username.label in the form
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    verifyPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    kitchenName = StringField('Kitchen Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    closeTime = TimeField('Close Time', validators=[DataRequired()])
    openTime = TimeField('Open Time', validators=[DataRequired()])
    deliveryOpenTime = TimeField('Delivery Open Time', validators=[DataRequired()])
    deliveryCloseTime = TimeField('Delivery Close Time', validators=[DataRequired()])
    transport = RadioField('Transport', choices=[('pickup','Pickup'),('delivery','Delivery')], validators=[DataRequired()])
    storage = RadioField('Storage', choices=[('Reusable','reusable'),('Disposable','Disposable')], validators=[DataRequired()])
    cancellation = RadioField('Cancellation', choices=[('canCancel','Cancel only within ordering hours'),('cannotCancel','Cancellations not allowed')], validators=[DataRequired()])
    # pickup = BooleanField('Pickup', validators=[DataRequired()])
    # delivery = BooleanField('Delivery', validators=[DataRequired()])
    # reusable = BooleanField('Reusable', validators=[DataRequired()])
    # disposable = BooleanField('Disposable', validators=[DataRequired()])
    # canCancel = BooleanField('Can Cancel', validators=[DataRequired()])
    submit = SubmitField('Sign Up') # SubmitField must allow Signup as its button Label.  Not sure yet where the action goes

    def validate_username(self, username):
        username = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'username'
                },
                ExpressionAttributeValues={
                    ':val': {'S': username}
                }
            )
        if username.get('Items') != []:
            raise ValidationError('That username is taken. Please choose another one.')

    def validate_email(self, email):
        email = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'email'
                },
                ExpressionAttributeValues={
                    ':val': {'S': email}
                }
            )
        if email.get('Items') != []:
            raise ValidationError('That email is taken. Please choose another one.')

    def validate_kitchen(self, kitchen):
        kitchen = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'kitchen_name'
                },
                ExpressionAttributeValues={
                    ':val': {'S': kitchen_name}
                }
            )
        if kitchen.get('Items') != []:
            raise ValidationError('That kitchen name is taken. Please choose another one.')

    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtfforms
    def validate_phone(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(phoneNumber)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(phoneNumber)):
                raise ValidationError('Invalid phone number.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login In')

class UpdateAccountForm(FlaskForm): # create a Registration Form class.  Below are the form fields
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])  # StringField must identify Username as the label so form.username.label takes you to the username.label in the form
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update') # SubmitField must allow Signup as its button Label.  Not sure yet where the action goes

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose another one.')

from main import db, s3
