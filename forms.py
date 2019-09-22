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
    kitchenName = StringField('Business Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    isDeliveringSunday = BooleanField('Sunday')
    isDeliveringMonday = BooleanField('Monday')
    isDeliveringTuesday = BooleanField('Tuesday')
    isDeliveringWednesday = BooleanField('Wednesday')
    isDeliveringThursday = BooleanField('Thursday')
    isDeliveringFriday = BooleanField('Friday')
    isDeliveringSaturday = BooleanField('Saturday')
    deliveryOpenTimeSunday = TimeField('Delivery Open Time Sunday')
    deliveryOpenTimeMonday = TimeField('Delivery Open Time Monday')
    deliveryOpenTimeTuesday = TimeField('Delivery Open Time Tuesday')
    deliveryOpenTimeWednesday = TimeField('Delivery Open Time Wednesday')
    deliveryOpenTimeThursday = TimeField('Delivery Open Time Thursday')
    deliveryOpenTimeFriday = TimeField('Delivery Open Time Friday')
    deliveryOpenTimeSaturday = TimeField('Delivery Open Time Saturday')
    deliveryCloseTimeSunday = TimeField('Delivery Close Time Sunday')
    deliveryCloseTimeMonday = TimeField('Delivery Close Time Monday')
    deliveryCloseTimeTuesday = TimeField('Delivery Close Time Tuesday')
    deliveryCloseTimeWednesday = TimeField('Delivery Close Time Wednesday')
    deliveryCloseTimeThursday = TimeField('Delivery Close Time Thursday')
    deliveryCloseTimeFriday = TimeField('Delivery Close Time Friday')
    deliveryCloseTimeSaturday = TimeField('Delivery Close Time Saturday')
    isAccepting24hr = BooleanField('24 Hours')
    isAcceptingSunday = BooleanField('Sunday')
    isAcceptingMonday = BooleanField('Monday')
    isAcceptingTuesday = BooleanField('Tuesday')
    isAcceptingWednesday = BooleanField('Wednesday')
    isAcceptingThursday = BooleanField('Thursday')
    isAcceptingFriday = BooleanField('Friday')
    isAcceptingSaturday = BooleanField('Saturday')
    acceptingOpenTimeSunday = TimeField('Sunday')
    acceptingOpenTimeMonday = TimeField('Monday')
    acceptingOpenTimeTuesday = TimeField('Tuesday')
    acceptingOpenTimeWednesday = TimeField('Wednesday')
    acceptingOpenTimeThursday = TimeField('Thursday')
    acceptingOpenTimeFriday = TimeField('Friday')
    acceptingOpenTimeSaturday = TimeField('Saturday')
    acceptingCloseTimeSunday = TimeField('Sunday')
    acceptingCloseTimeMonday = TimeField('Monday')
    acceptingCloseTimeTuesday = TimeField('Tuesday')
    acceptingCloseTimeWednesday = TimeField('Wednesday')
    acceptingCloseTimeThursday = TimeField('Thursday')
    acceptingCloseTimeFriday = TimeField('Friday')
    acceptingCloseTimeSaturday = TimeField('Saturday')
    transport = RadioField('Delivery Strategy', choices=[('pickup','Pickup at Farmers Market'),('delivery','Deliver to Customer')], validators=[DataRequired()])
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

    def validate_acceptingOpenTimeMonday(self, acceptingOpenTimeMonday):
        if self.acceptingOpenTimeMonday.data and self.acceptingCloseTimeMonday.data:
            if self.acceptingOpenTimeMonday.data > self.acceptingCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeMonday(self, acceptingCloseTimeMonday):
        if self.acceptingOpenTimeMonday.data and self.acceptingCloseTimeMonday.data:
            if self.acceptingOpenTimeMonday.data > self.acceptingCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeTuesday(self, acceptingOpenTimeTuesday):
        if self.acceptingOpenTimeTuesday.data and self.acceptingCloseTimeTuesday.data:
            if self.acceptingOpenTimeTuesday.data > self.acceptingCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeTuesday(self, acceptingCloseTimeTuesday):
        if self.acceptingOpenTimeTuesday.data and self.acceptingCloseTimeTuesday.data:
            if self.acceptingOpenTimeTuesday.data > self.acceptingCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeWednesday(self, acceptingOpenTimeWednesday):
        if self.acceptingOpenTimeWednesday.data and self.acceptingCloseTimeWednesday.data:
            if self.acceptingOpenTimeWednesday.data > self.acceptingCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeWednesday(self, acceptingCloseTimeWednesday):
        if self.acceptingOpenTimeWednesday.data and self.acceptingCloseTimeWednesday.data:
            if self.acceptingOpenTimeWednesday.data > self.acceptingCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeThursday(self, acceptingOpenTimeThursday):
        if self.acceptingOpenTimeThursday.data and self.acceptingCloseTimeThursday.data:
            if self.acceptingOpenTimeThursday.data > self.acceptingCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeThursday(self, acceptingCloseTimeThursday):
        if self.acceptingOpenTimeThursday.data and self.acceptingCloseTimeThursday.data:
            if self.acceptingOpenTimeThursday.data > self.acceptingCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeFriday(self, acceptingOpenTimeFriday):
        if self.acceptingOpenTimeFriday.data and self.acceptingCloseTimeFriday.data:
            if self.acceptingOpenTimeFriday.data > self.acceptingCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeFriday(self, acceptingCloseTimeFriday):
        if self.acceptingOpenTimeFriday.data and self.acceptingCloseTimeFriday.data:
            if self.acceptingOpenTimeFriday.data > self.acceptingCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeSaturday(self, acceptingOpenTimeSaturday):
        if self.acceptingOpenTimeSaturday.data and self.acceptingCloseTimeSaturday.data:
            if self.acceptingOpenTimeSaturday.data > self.acceptingCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeSaturday(self, acceptingCloseTimeSaturday):
        if self.acceptingOpenTimeSaturday.data and self.acceptingCloseTimeSaturday.data:
            if self.acceptingOpenTimeSaturday.data > self.acceptingCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeSunday(self, acceptingOpenTimeSunday):
        if self.acceptingOpenTimeSunday.data and self.acceptingCloseTimeSunday.data:
            if self.acceptingOpenTimeSunday.data > self.acceptingCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeSunday(self, acceptingCloseTimeSunday):
        if self.acceptingOpenTimeSunday.data and self.acceptingCloseTimeSunday.data:
            if self.acceptingOpenTimeSunday.data > self.acceptingCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeMonday(self, deliveryOpenTimeMonday):
        if self.deliveryOpenTimeMonday.data and self.deliveryCloseTimeMonday.data:
            if self.deliveryOpenTimeMonday.data > self.deliveryCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeMonday(self, deliveryCloseTimeMonday):
        if self.deliveryOpenTimeMonday.data and self.deliveryCloseTimeMonday.data:
            if self.deliveryOpenTimeMonday.data > self.deliveryCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeTuesday(self, deliveryOpenTimeTuesday):
        if self.deliveryOpenTimeTuesday.data and self.deliveryCloseTimeTuesday.data:
            if self.deliveryOpenTimeTuesday.data > self.deliveryCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeTuesday(self, deliveryCloseTimeTuesday):
        if self.deliveryOpenTimeTuesday.data and self.deliveryCloseTimeTuesday.data:
            if self.deliveryOpenTimeTuesday.data > self.deliveryCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeWednesday(self, deliveryOpenTimeWednesday):
        if self.deliveryOpenTimeWednesday.data and self.deliveryCloseTimeWednesday.data:
            if self.deliveryOpenTimeWednesday.data > self.deliveryCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeWednesday(self, deliveryCloseTimeWednesday):
        if self.deliveryOpenTimeWednesday.data and self.deliveryCloseTimeWednesday.data:
            if self.deliveryOpenTimeWednesday.data > self.deliveryCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeThursday(self, deliveryOpenTimeThursday):
        if self.deliveryOpenTimeThursday.data and self.deliveryCloseTimeThursday.data:
            if self.deliveryOpenTimeThursday.data > self.deliveryCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeThursday(self, deliveryCloseTimeThursday):
        if self.deliveryOpenTimeThursday.data and self.deliveryCloseTimeThursday.data:
            if self.deliveryOpenTimeThursday.data > self.deliveryCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeFriday(self, deliveryOpenTimeFriday):
        if self.deliveryOpenTimeFriday.data and self.deliveryCloseTimeFriday.data:
            if self.deliveryOpenTimeFriday.data > self.deliveryCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeFriday(self, deliveryCloseTimeFriday):
        if self.deliveryOpenTimeFriday.data and self.deliveryCloseTimeFriday.data:
            if self.deliveryOpenTimeFriday.data > self.deliveryCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeSaturday(self, deliveryOpenTimeSaturday):
        if self.deliveryOpenTimeSaturday.data and self.deliveryCloseTimeSaturday.data:
            if self.deliveryOpenTimeSaturday.data > self.deliveryCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeSaturday(self, deliveryCloseTimeSaturday):
        if self.deliveryOpenTimeSaturday.data and self.deliveryCloseTimeSaturday.data:
            if self.deliveryOpenTimeSaturday.data > self.deliveryCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeSunday(self, deliveryOpenTimeSunday):
        if self.deliveryOpenTimeSunday.data and self.deliveryCloseTimeSunday.data:
            if self.deliveryOpenTimeSunday.data > self.deliveryCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeSunday(self, deliveryCloseTimeSunday):
        if self.deliveryOpenTimeSunday.data and self.deliveryCloseTimeSunday.data:
            if self.deliveryOpenTimeSunday.data > self.deliveryCloseTimeSunday.data:
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

class CustomerForm(FlaskForm):
    representative = StringField('Representative')
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    betaTester = RadioField('Would you like to be a Beta Tester?', choices=[('True','Yes'),('False','No')], default='True', validators=[DataRequired()])
    futureCustomer = RadioField('Would you like to be a Future Customer?', choices=[('True','Yes'),('False','No')], default='True', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = db.scan(TableName='customers',
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'email'
                },
                ExpressionAttributeValues={
                    ':val': {'S': email.data.lower()}
                }
            )
        if user.get('Items') != []:
            raise ValidationError('It looks like the email: '+ email.data + ' has already been registered.')

    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtfforms
    def validate_phoneNumber(self, phoneNumber):
        user = db.scan(TableName="customers",
                FilterExpression='#name = :val',
                ExpressionAttributeNames={
                    '#name': 'phone_number'
                },
                ExpressionAttributeValues={
                    ':val': {'S': phoneNumber.data}
                }
            )
        if user.get('Items') != []:
            raise ValidationError('It looks like the phone number: '+ phoneNumber.data + ' has already been registered.')

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

class UpdateAccountForm(FlaskForm): # create a Registration Form class.  Below are the form fields
    cancellation = RadioField('Cancellation', choices=[('canCancel','Allow cancellation within ordering hours'),('cannotCancel','Cancellations not allowed')], validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    isDeliveringSunday = BooleanField('Sunday')
    isDeliveringMonday = BooleanField('Monday')
    isDeliveringTuesday = BooleanField('Tuesday')
    isDeliveringWednesday = BooleanField('Wednesday')
    isDeliveringThursday = BooleanField('Thursday')
    isDeliveringFriday = BooleanField('Friday')
    isDeliveringSaturday = BooleanField('Saturday')
    deliveryOpenTimeSunday = TimeField('Delivery Open Time Sunday')
    deliveryOpenTimeMonday = TimeField('Delivery Open Time Monday')
    deliveryOpenTimeTuesday = TimeField('Delivery Open Time Tuesday')
    deliveryOpenTimeWednesday = TimeField('Delivery Open Time Wednesday')
    deliveryOpenTimeThursday = TimeField('Delivery Open Time Thursday')
    deliveryOpenTimeFriday = TimeField('Delivery Open Time Friday')
    deliveryOpenTimeSaturday = TimeField('Delivery Open Time Saturday')
    deliveryCloseTimeSunday = TimeField('Delivery Close Time Sunday')
    deliveryCloseTimeMonday = TimeField('Delivery Close Time Monday')
    deliveryCloseTimeTuesday = TimeField('Delivery Close Time Tuesday')
    deliveryCloseTimeWednesday = TimeField('Delivery Close Time Wednesday')
    deliveryCloseTimeThursday = TimeField('Delivery Close Time Thursday')
    deliveryCloseTimeFriday = TimeField('Delivery Close Time Friday')
    deliveryCloseTimeSaturday = TimeField('Delivery Close Time Saturday')
    isAccepting24hr = BooleanField('24 Hours')
    isAcceptingSunday = BooleanField('Sunday')
    isAcceptingMonday = BooleanField('Monday')
    isAcceptingTuesday = BooleanField('Tuesday')
    isAcceptingWednesday = BooleanField('Wednesday')
    isAcceptingThursday = BooleanField('Thursday')
    isAcceptingFriday = BooleanField('Friday')
    isAcceptingSaturday = BooleanField('Saturday')
    acceptingOpenTimeSunday = TimeField('Sunday')
    acceptingOpenTimeMonday = TimeField('Monday')
    acceptingOpenTimeTuesday = TimeField('Tuesday')
    acceptingOpenTimeWednesday = TimeField('Wednesday')
    acceptingOpenTimeThursday = TimeField('Thursday')
    acceptingOpenTimeFriday = TimeField('Friday')
    acceptingOpenTimeSaturday = TimeField('Saturday')
    acceptingCloseTimeSunday = TimeField('Sunday')
    acceptingCloseTimeMonday = TimeField('Monday')
    acceptingCloseTimeTuesday = TimeField('Tuesday')
    acceptingCloseTimeWednesday = TimeField('Wednesday')
    acceptingCloseTimeThursday = TimeField('Thursday')
    acceptingCloseTimeFriday = TimeField('Friday')
    acceptingCloseTimeSaturday = TimeField('Saturday')
    description = TextAreaField('Description', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstName = StringField('First Name', validators=[DataRequired()])
    kitchenName = StringField('Business Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    storage = RadioField('Delivery Container', choices=[('reusable','Reusable'),('disposable','Disposable')], validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    storage = RadioField('Storage', choices=[('reusable','Reusable'),('disposable','Disposable')], validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    transport = RadioField('Delivery Strategy', choices=[('pickup','Pickup at Farmers Market'),('delivery','Deliver to Customer')], validators=[DataRequired()])
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

    def validate_acceptingOpenTimeMonday(self, acceptingOpenTimeMonday):
        if self.acceptingOpenTimeMonday.data and self.acceptingCloseTimeMonday.data:
            if self.acceptingOpenTimeMonday.data > self.acceptingCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeMonday(self, acceptingCloseTimeMonday):
        if self.acceptingOpenTimeMonday.data and self.acceptingCloseTimeMonday.data:
            if self.acceptingOpenTimeMonday.data > self.acceptingCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeTuesday(self, acceptingOpenTimeTuesday):
        if self.acceptingOpenTimeTuesday.data and self.acceptingCloseTimeTuesday.data:
            if self.acceptingOpenTimeTuesday.data > self.acceptingCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeTuesday(self, acceptingCloseTimeTuesday):
        if self.acceptingOpenTimeTuesday.data and self.acceptingCloseTimeTuesday.data:
            if self.acceptingOpenTimeTuesday.data > self.acceptingCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeWednesday(self, acceptingOpenTimeWednesday):
        if self.acceptingOpenTimeWednesday.data and self.acceptingCloseTimeWednesday.data:
            if self.acceptingOpenTimeWednesday.data > self.acceptingCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeWednesday(self, acceptingCloseTimeWednesday):
        if self.acceptingOpenTimeWednesday.data and self.acceptingCloseTimeWednesday.data:
            if self.acceptingOpenTimeWednesday.data > self.acceptingCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeThursday(self, acceptingOpenTimeThursday):
        if self.acceptingOpenTimeThursday.data and self.acceptingCloseTimeThursday.data:
            if self.acceptingOpenTimeThursday.data > self.acceptingCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeThursday(self, acceptingCloseTimeThursday):
        if self.acceptingOpenTimeThursday.data and self.acceptingCloseTimeThursday.data:
            if self.acceptingOpenTimeThursday.data > self.acceptingCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeFriday(self, acceptingOpenTimeFriday):
        if self.acceptingOpenTimeFriday.data and self.acceptingCloseTimeFriday.data:
            if self.acceptingOpenTimeFriday.data > self.acceptingCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeFriday(self, acceptingCloseTimeFriday):
        if self.acceptingOpenTimeFriday.data and self.acceptingCloseTimeFriday.data:
            if self.acceptingOpenTimeFriday.data > self.acceptingCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeSaturday(self, acceptingOpenTimeSaturday):
        if self.acceptingOpenTimeSaturday.data and self.acceptingCloseTimeSaturday.data:
            if self.acceptingOpenTimeSaturday.data > self.acceptingCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeSaturday(self, acceptingCloseTimeSaturday):
        if self.acceptingOpenTimeSaturday.data and self.acceptingCloseTimeSaturday.data:
            if self.acceptingOpenTimeSaturday.data > self.acceptingCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingOpenTimeSunday(self, acceptingOpenTimeSunday):
        if self.acceptingOpenTimeSunday.data and self.acceptingCloseTimeSunday.data:
            if self.acceptingOpenTimeSunday.data > self.acceptingCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_acceptingCloseTimeSunday(self, acceptingCloseTimeSunday):
        if self.acceptingOpenTimeSunday.data and self.acceptingCloseTimeSunday.data:
            if self.acceptingOpenTimeSunday.data > self.acceptingCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeMonday(self, deliveryOpenTimeMonday):
        if self.deliveryOpenTimeMonday.data and self.deliveryCloseTimeMonday.data:
            if self.deliveryOpenTimeMonday.data > self.deliveryCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeMonday(self, deliveryCloseTimeMonday):
        if self.deliveryOpenTimeMonday.data and self.deliveryCloseTimeMonday.data:
            if self.deliveryOpenTimeMonday.data > self.deliveryCloseTimeMonday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeTuesday(self, deliveryOpenTimeTuesday):
        if self.deliveryOpenTimeTuesday.data and self.deliveryCloseTimeTuesday.data:
            if self.deliveryOpenTimeTuesday.data > self.deliveryCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeTuesday(self, deliveryCloseTimeTuesday):
        if self.deliveryOpenTimeTuesday.data and self.deliveryCloseTimeTuesday.data:
            if self.deliveryOpenTimeTuesday.data > self.deliveryCloseTimeTuesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeWednesday(self, deliveryOpenTimeWednesday):
        if self.deliveryOpenTimeWednesday.data and self.deliveryCloseTimeWednesday.data:
            if self.deliveryOpenTimeWednesday.data > self.deliveryCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeWednesday(self, deliveryCloseTimeWednesday):
        if self.deliveryOpenTimeWednesday.data and self.deliveryCloseTimeWednesday.data:
            if self.deliveryOpenTimeWednesday.data > self.deliveryCloseTimeWednesday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeThursday(self, deliveryOpenTimeThursday):
        if self.deliveryOpenTimeThursday.data and self.deliveryCloseTimeThursday.data:
            if self.deliveryOpenTimeThursday.data > self.deliveryCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeThursday(self, deliveryCloseTimeThursday):
        if self.deliveryOpenTimeThursday.data and self.deliveryCloseTimeThursday.data:
            if self.deliveryOpenTimeThursday.data > self.deliveryCloseTimeThursday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeFriday(self, deliveryOpenTimeFriday):
        if self.deliveryOpenTimeFriday.data and self.deliveryCloseTimeFriday.data:
            if self.deliveryOpenTimeFriday.data > self.deliveryCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeFriday(self, deliveryCloseTimeFriday):
        if self.deliveryOpenTimeFriday.data and self.deliveryCloseTimeFriday.data:
            if self.deliveryOpenTimeFriday.data > self.deliveryCloseTimeFriday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeSaturday(self, deliveryOpenTimeSaturday):
        if self.deliveryOpenTimeSaturday.data and self.deliveryCloseTimeSaturday.data:
            if self.deliveryOpenTimeSaturday.data > self.deliveryCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeSaturday(self, deliveryCloseTimeSaturday):
        if self.deliveryOpenTimeSaturday.data and self.deliveryCloseTimeSaturday.data:
            if self.deliveryOpenTimeSaturday.data > self.deliveryCloseTimeSaturday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryOpenTimeSunday(self, deliveryOpenTimeSunday):
        if self.deliveryOpenTimeSunday.data and self.deliveryCloseTimeSunday.data:
            if self.deliveryOpenTimeSunday.data > self.deliveryCloseTimeSunday.data:
                raise ValidationError('Please choose valid times.')

    def validate_deliveryCloseTimeSunday(self, deliveryCloseTimeSunday):
        if self.deliveryOpenTimeSunday.data and self.deliveryCloseTimeSunday.data:
            if self.deliveryOpenTimeSunday.data > self.deliveryCloseTimeSunday.data:
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
