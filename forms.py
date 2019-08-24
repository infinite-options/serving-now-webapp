#  Prashant Marathay
#  Flask Tutorial Video 3  https://www.youtube.com/watch?v=UIJKdCIEXUQ
#  Most everything is available in wt forms
#  Could go into main application file but better to break out
#  Write python class that will automatically be converted into html form in the template (1:55)
import phonenumbers
import datetime

from flask_wtf import FlaskForm # imports to
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask import session as login_session
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TimeField, RadioField, TextAreaField # imports these classes
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import check_password_hash

class RegistrationForm(FlaskForm): # create a Registration Form class.  Below are the form fields
    kitchenName = StringField('Buisness Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    closeTime = TimeField('Close Time', validators=[DataRequired()])
    openTime = TimeField('Open Time', validators=[DataRequired()])
    deliveryOpenTime = TimeField('Delivery Open Time', validators=[DataRequired()])
    deliveryCloseTime = TimeField('Delivery Close Time', validators=[DataRequired()])
    transport = RadioField('Transport', choices=[('pickup','Pickup'),('delivery','Delivery')], validators=[DataRequired()])
    storage = RadioField('Delivery Container', choices=[('reusable','Reusable'),('disposable','Disposable')], validators=[DataRequired()])
    cancellation = RadioField('Cancellation', choices=[('canCancel','Allow cancellation within ordering hours'),('cannotCancel','Cancellations not allowed')], validators=[DataRequired()])
    kitchenImage = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
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
    # pickup = BooleanField('Pickup', validators=[DataRequired()])
    # delivery = BooleanField('Delivery', validators=[DataRequired()])
    # reusable = BooleanField('Reusable', validators=[DataRequired()])
    # disposable = BooleanField('Disposable', validators=[DataRequired()])
    # canCancel = BooleanField('Can Cancel', validators=[DataRequired()])
    submit = SubmitField('Sign Up') # SubmitField must allow Signup as its button Label.  Not sure yet where the action goes

    def validate_transport(self, transport):
        if self.transport.data == 'None':
            raise ValidationError('Please pick either Pickup or Delivery')

    def validate_storage(self, storage):
        if self.storage.data == 'None':
            raise ValidationError('Please pick either Reusable or Disposale')

    def validate_cancellation(self, cancellation):
        if self.cancellation.data == 'None':
            raise ValidationError('Please pick a cancellation option')

    def validate_openTime(self, openTime):
        if self.openTime.data >= self.closeTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_closeTime(self, closeTime):
        if self.openTime.data >= self.closeTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTime(self, deliveryOpenTime):
        if self.deliveryOpenTime.data >= self.deliveryCloseTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTime(self, deliveryCloseTime):
        if self.deliveryOpenTime.data >= self.deliveryCloseTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_email(self, email):
        user = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'email'
                },
                ExpressionAttributeValues={
                    ':val': {'S': email.data.lower()}
                }
            )
        if user.get('Items') != []:
            raise ValidationError('That email is taken. Please choose another one.')


    def validate_kitchenName(self, kitchenName):
        user = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'kitchen_name'
                },
                ExpressionAttributeValues={
                    ':val': {'S': kitchenName.data}
                }
            )
        if user.get('Items') != []:
            raise ValidationError('That kitchen name is taken. Please choose another one.')

    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtfforms
    def validate_phoneNumber(self, phoneNumber):
        if len(phoneNumber.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(phoneNumber.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+phoneNumber.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate(self):
        if not super(LoginForm, self).validate():
            return False
        user = db.scan(TableName="kitchens",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'email'
                },
                ExpressionAttributeValues={
                    ':val': {'S': self.email.data.lower()}
                }
            )
        if user.get('Items') == []:
            self.email.errors.append(self.email.data + ' has not been registered with Serving Now.')
            return False
        if user.get('Items') != []:
            if not check_password_hash(user['Items'][0]['password']['S'], \
              self.password.data):
                self.password.errors.append('Invalid Password, please try again.')
                return False
        return True


class UpdateAccountForm(FlaskForm): # create a Registration Form class.  Below are the form fields
    closeTime = TimeField('Close Time', validators=[DataRequired()])
    cancellation = RadioField('Cancellation', choices=[('canCancel','Allow cancellation within ordering hours'),('cannotCancel','Cancellations not allowed')], validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    deliveryOpenTime = TimeField('Delivery Open Time', validators=[DataRequired()])
    deliveryCloseTime = TimeField('Delivery Close Time', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    kitchenName = StringField('Buisness Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    openTime = TimeField('Open Time', validators=[DataRequired()])
    storage = RadioField('Delivery Container', choices=[('reusable','Reusable'),('disposable','Disposable')], validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    storage = RadioField('Storage', choices=[('reusable','Reusable'),('disposable','Disposable')], validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    transport = RadioField('Transport', choices=[('pickup','Pickup'),('delivery','Delivery')], validators=[DataRequired()])
    kitchenImage = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    submit = SubmitField('Update') # SubmitField must allow Signup as its button Label.  Not sure yet where the action goes
    # password = PasswordField('New Password', validators=[DataRequired()])
    # verifyPassword = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    # pickup = BooleanField('Pickup', validators=[DataRequired()])
    # delivery = BooleanField('Delivery', validators=[DataRequired()])
    # reusable = BooleanField('Reusable', validators=[DataRequired()])
    # disposable = BooleanField('Disposable', validators=[DataRequired()])
    # canCancel = BooleanField('Can Cancel', validators=[DataRequired()])

    def validate_transport(self, transport):
        if self.transport.data == 'None':
            raise ValidationError('Please pick either Pickup or Delivery')

    def validate_storage(self, storage):
        if self.storage.data == 'None':
            raise ValidationError('Please pick either Reusable or Disposale')

    def validate_cancellation(self, cancellation):
        if self.cancellation.data == 'None':
            raise ValidationError('Please pick a cancellation option')

    def validate_openTime(self, openTime):
        if self.openTime.data >= self.closeTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_closeTime(self, closeTime):
        if self.openTime.data >= self.closeTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTime(self, deliveryOpenTime):
        if self.deliveryOpenTime.data >= self.deliveryCloseTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTime(self, deliveryCloseTime):
        if self.deliveryOpenTime.data >= self.deliveryCloseTime.data:
            raise ValidationError('Please choose valid times.')

    def validate_email(self, email):
        if email.data.lower() != login_session['email']:
            user = db.scan(TableName="kitchens",
                    FilterExpression='#name = :val',
                    ExpressionAttributeNames={
                        '#name': 'email'
                    },
                    ExpressionAttributeValues={
                        ':val': {'S': email.data.lower()}
                    }
                )
            if user.get('Items') != []:
                raise ValidationError('That email is taken. Please choose another one.')


    def validate_kitchenName(self, kitchenName):
        if kitchenName.data != login_session['kitchen_name']:
            user = db.scan(TableName="kitchens",
                    FilterExpression='#name = :val',
                    ExpressionAttributeNames={
                        '#name': 'kitchen_name'
                    },
                    ExpressionAttributeValues={
                        ':val': {'S': kitchenName.data}
                    }
                )
            if user.get('Items') != []:
                raise ValidationError('That kitchen name is taken. Please choose another one.')


from main import db, s3
