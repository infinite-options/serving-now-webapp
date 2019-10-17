# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-24 19:40:12
# @Last Modified by:   Prashant Marathay
# @Last Modified time: 2019-07-26 19:10:31
import boto3
import json
import uuid
import requests
import locale
import sys

from datetime import datetime, time
from pytz import timezone
from operator import itemgetter

from flask import (Flask, Blueprint, request, render_template,
    redirect, url_for, flash)
from flask import session as login_session
from flask_cors import CORS, cross_origin
from flask_caching import Cache
from flask_login import (LoginManager, login_required, current_user,
	UserMixin, login_user, logout_user)
from flask_mail import Mail, Message
from PIL import Image


from forms import RegistrationForm, LoginForm, UpdateAccountForm, CustomerForm


from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import (generate_password_hash,
    check_password_hash)


app = Flask(__name__, static_folder='static', template_folder='templates')
cors = CORS(app, resources={r'/api/*': {'origins': '*'}}, support_credentials=True)

login_manager = LoginManager(app)

secret_key = 'app_secret_key'

app.config['SECRET_KEY'] = secret_key
app.config['MAIL_USERNAME'] = 'infiniteoptions.meals@gmail.com'
app.config['MAIL_PASSWORD'] = 'annApurna'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CACHE_TYPE'] = 'null'
cache = Cache(app,config={'CACHE_TYPE': 'redis'})

cache.init_app(app)

mail = Mail(app)

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

# db = boto3.client('dynamodb',
#           region_name='us-west-1',
#           aws_access_key_id=AWS_KEY_ID,
#           aws_secret_access_key=AWS_SECRET_KEY)
#
# s3 = boto3.client('s3',
#     aws_access_key_id=AWS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_KEY)


# aws s3 bucket where the image is stored
BUCKET_NAME = 'servingnow'

API_BASE_URL = 'https://phaqvwjbw6.execute-api.us-west-1.amazonaws.com/dev'
# API_BASE_URL = 'http://localhost:5000'

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    '''
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    '''
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============

def upload_s3_img(file, bucket, key):
    if file and allowed_file(file.filename):
        filename = 'https://s3-us-west-1.amazonaws.com/' \
                   + str(bucket) + '/' + str(key)
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        return filename
    return None

# ===========================================================

def strToBool(str):
    if str == 'true' or str == 'True':
        return True
    return False


def allowed_file(filename):
    '''Checks if the file is allowed to upload'''
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =======HELPER FUNCTIONS FOR DELETING AN IMAGE=============

def delete_s3_img(bucket, key):
    print ('Inside delete_s3_img..')
    print ('bucket: ', bucket)
    print ('key: ', key)

    try:
        delete_file = s3.delete_object(
                            Bucket=bucket,
                            Key=key)
        print('delete_file : ', delete_file)

    except:
        print ('Item cannot be deleted')

    return None
# ===========================================================



class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        return User(user_id)


@login_manager.user_loader
def _login_manager_load_user(user_id):
    return User.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/payment/<string:order_id>/<string:total>')
def payment(order_id, total):
    return render_template('paypal.html', total=total, order_id=order_id)

@app.route('/paymentComplete')
def paymentComplete():
    return render_template('paymentComplete.html')

@app.route('/order/<string:order_id>/paymentCancelled')
def paymentCancelled(order_id):
    message = ''
    deleted_order = db.scan(TableName='meal_orders',
                            FilterExpression='order_id = :value',
                            ExpressionAttributeValues={
                                ':value': {'S': order_id},
                                }
                            )
    if deleted_order.get('Items') != []:
        if deleted_order['Items'][0]['status']['S'] == 'delivered':
            message = 'Sorry, your order has been delivered and cannot be cancelled.'
        else:
            db.delete_item(TableName='meal_orders', Key={'order_id': {'S': order_id}})
            message = 'Your order has been cancelled.'
    else:
        message = 'The order you are trying to delete does not exist.'
    return render_template('paymentCancelled.html', message=message)

@app.route('/accounts/logout')
@login_required
def logout():
    del login_session['user_id']
    del login_session['kitchen_name']
    logout_user()
    return redirect(url_for('index'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Home')

@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('kitchen', id=login_session['user_id']))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        try:
            user = db.query(TableName='kitchens',
                IndexName='email-index',
                Limit=1,
                KeyConditionExpression='email = :val',
                ExpressionAttributeValues={
                    ':val': {'S': email}
                }
            )

            if user.get('Count') == 0:
                return render_template('login.html', title='Login', form=form)

            if not check_password_hash(user['Items'][0]['password']['S'], \
              password):
                return render_template('login.html', title='Login', form=form)
            else:
                user_id = user['Items'][0]['kitchen_id']['S']
                login_session['kitchen_name'] = user['Items'][0]['kitchen_name']['S']
                login_session['user_id'] = user_id
                login_session['email'] = email
                login_user(User(user_id))
                return redirect(url_for('kitchen', id=login_session['user_id']))

        except Exception as e:
            print(e)
            return render_template('login.html', title='Login', form=form)
    return render_template('login.html', title='Login', form=form)

@app.route('/accounts/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RegistrationForm(request.form)
    defaultTime = time(0, 0, 0)
    form.deliveryOpenTimeSunday.data = time(10, 0, 0)
    form.deliveryOpenTimeMonday.data = defaultTime
    form.deliveryOpenTimeTuesday.data = defaultTime
    form.deliveryOpenTimeWednesday.data = time(10, 0, 0)
    form.deliveryOpenTimeThursday.data = defaultTime
    form.deliveryOpenTimeFriday.data = defaultTime
    form.deliveryOpenTimeSaturday.data = defaultTime
    form.acceptingOpenTimeSunday.data = defaultTime
    form.acceptingOpenTimeMonday.data = defaultTime
    form.acceptingOpenTimeTuesday.data = defaultTime
    form.acceptingOpenTimeWednesday.data = defaultTime
    form.acceptingOpenTimeThursday.data = defaultTime
    form.acceptingOpenTimeFriday.data = defaultTime
    form.acceptingOpenTimeSaturday.data = defaultTime
    form.deliveryCloseTimeSunday.data = time(14, 0, 0)
    form.deliveryCloseTimeMonday.data = defaultTime
    form.deliveryCloseTimeTuesday.data = defaultTime
    form.deliveryCloseTimeWednesday.data = time(14, 0, 0)
    form.deliveryCloseTimeThursday.data = defaultTime
    form.deliveryCloseTimeFriday.data = defaultTime
    form.deliveryCloseTimeSaturday.data = defaultTime
    form.acceptingCloseTimeSunday.data = defaultTime
    form.acceptingCloseTimeMonday.data = defaultTime
    form.acceptingCloseTimeTuesday.data = defaultTime
    form.acceptingCloseTimeWednesday.data = defaultTime
    form.acceptingCloseTimeThursday.data = defaultTime
    form.acceptingCloseTimeFriday.data = defaultTime
    form.acceptingCloseTimeSaturday.data = defaultTime
    form.isDeliveringWednesday.data = True
    form.isDeliveringSunday.data = True
    form.isAccepting24hr.data = True
    if form.validate_on_submit():
        delivery = False
        pickup = False
        disposable = False
        reusable = False
        canCancel = False
        if form.transport.data == 'delivery':
            delivery = True
        if form.transport.data == 'pickup':
            pickup = True
        if form.storage.data == 'disposable':
            disposable = True
        if form.storage.data == 'reusable':
            reusable = True
        if form.cancellation.data == 'canCancel':
            canCancel = True

        acceptingHours = [ {'M': {'is_accepting': {'BOOL':form.isAcceptingSunday.data},
                                  'open_time': {'S':form.acceptingOpenTimeSunday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeSunday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingMonday.data},
                                  'open_time': {'S':form.acceptingOpenTimeMonday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeMonday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingTuesday.data},
                                  'open_time': {'S':form.acceptingOpenTimeTuesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeTuesday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingWednesday.data},
                                  'open_time': {'S':form.acceptingOpenTimeWednesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeWednesday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingThursday.data},
                                  'open_time': {'S':form.acceptingOpenTimeThursday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeThursday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingFriday.data},
                                  'open_time': {'S':form.acceptingOpenTimeFriday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeFriday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingSaturday.data},
                                  'open_time': {'S':form.acceptingOpenTimeSaturday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeSaturday.data.strftime('%H:%M')}}}]

        deliveryHours =   [{'M': {'is_delivering': {'BOOL':form.isAcceptingSunday.data},
                                  'open_time': {'S':form.acceptingOpenTimeSunday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeSunday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringMonday.data},
                                  'open_time': {'S':form.deliveryOpenTimeMonday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeMonday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringTuesday.data},
                                  'open_time': {'S':form.deliveryOpenTimeTuesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeTuesday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringWednesday.data},
                                  'open_time': {'S':form.deliveryOpenTimeWednesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeWednesday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringThursday.data},
                                  'open_time': {'S':form.deliveryOpenTimeThursday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeThursday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringFriday.data},
                                  'open_time': {'S':form.deliveryOpenTimeFriday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeFriday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringSaturday.data},
                                  'open_time': {'S':form.deliveryOpenTimeSaturday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeSaturday.data.strftime('%H:%M')}}}]

        created_at = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')
        kitchen_id = uuid.uuid4().hex

        photoPath = 'https://servingnow.s3-us-west-1.amazonaws.com/kitchen_imgs/landing-logo.png'

        print('form.kitchenImage.data: ' + str(form.kitchenImage.data))

        if form.kitchenImage.data:
            photo_key = 'kitchen_imgs/{}'.format(str(kitchen_id))
            photoPath = upload_s3_img(form.kitchenImage.data, BUCKET_NAME, photo_key)

        add_kitchen = db.put_item(TableName='kitchens',
                    Item={'kitchen_id': {'S': kitchen_id},
                          'accepting_hours': {'L': acceptingHours},
                          'is_accepting_24hr': {'BOOL': form.isAccepting24hr.data},
                          'can_cancel': { 'BOOL': canCancel },
                          'city': {'S': form.city.data},
                          'close_time': {'S': form.acceptingCloseTimeMonday.data.strftime('%H:%M')},
                          'created_at': {'S': created_at},
                          'delivery': { 'BOOL': delivery},
                          'delivery_open_time': {'S': form.deliveryOpenTimeMonday.data.strftime('%H:%M')},
                          'delivery_close_time': {'S': form.deliveryCloseTimeMonday.data.strftime('%H:%M')},
                          'delivery_hours': {'L': deliveryHours},
                          'description': {'S': form.description.data},
                          'disposable': { 'BOOL': disposable},
                          'email': {'S': form.email.data.lower()},
                          'first_name': {'S': form.firstName.data},
                          'isOpen': {'BOOL': False},
                          'kitchen_image': {'S': photoPath},
                          'kitchen_name': {'S': form.kitchenName.data},
                          'last_name': {'S': form.lastName.data},
                          'open_time': {'S': form.acceptingOpenTimeMonday.data.strftime('%H:%M')},
                          'password': {'S': generate_password_hash(form.password.data)},
                          'phone_number': {'S': form.phoneNumber.data},
                          'pickup': { 'BOOL': pickup},
                          'reusable': { 'BOOL': reusable},
                          'st': {'S': form.state.data},
                          'street': {'S': form.street.data},
                          'zipcode': {'S': form.zipcode.data}
                    }
                )
        flash('Your account has been created! You are now able to log in.', 'success') # python 3 format.
        print('Account for ' + form.email.data + ' has been created')
        return redirect(url_for('login'))

    print(form.errors)

    return render_template('register.html', title='Register', form=form) #  This is what happens if the submit is unsuccessful with errors highlighted

@app.route('/customer/register', methods=['GET', 'POST'])
def registerCustomer():
    form = CustomerForm(request.form)
    if form.validate_on_submit():
        if not form.representative.data:
            form.representative.data = 'None'
        login_session['representative'] = form.representative.data
        customerId = uuid.uuid4().hex
        todaysDate = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')
        add_customer = db.put_item(TableName='customers',
                    Item={'customer_id': {'S': customerId},
                          'created_at': {'S': todaysDate},
                          'representative': {'S': form.representative.data},
                          'first_name': {'S': form.firstName.data},
                          'last_name': {'S': form.lastName.data},
                          'phone_number': {'S': form.phoneNumber.data},
                          'email': {'S': form.email.data.lower()},
                          'beta_tester': {'BOOL': strToBool(form.futureCustomer.data)},
                          'future_customer': {'BOOL': strToBool(form.futureCustomer.data)},
                    }
                )
        flash("Thank you " + form.firstName.data + ' is now registered as a customer for Serving Now.', 'success') # python 3 format.
        print('Account for ' + form.email.data + ' has been created')
        return redirect(url_for('home'))
    if login_session.get('representative'):
        form.representative.data = login_session['representative']
    return render_template('registerCustomer.html', title='registerCustomer', form=form) #  This is what happens if the submit is unsuccessful with errors highlighted


@app.route('/kitchens/<string:id>')
@login_required
def kitchen(id):
    # return render_template('kitchen.html')
    # if 'name' not in login_session:
    #     return redirect(url_for('index'))
    #
    kitchen_id = current_user.get_id()
    apiURL = API_BASE_URL +'/api/v1/meals/' + kitchen_id
    # apiURL = 'http://localhost:5000/api/v1/meals/' + current_user.get_id()

    # print('API URL: ' + str(apiURL))
    # apiURL = API_BASE_URL + '/api/v1/meals/' + '5d114cb5c4f54c94a8bb4d955a576fca'
    response = requests.get(apiURL)
    #
    allMeals = response.json().get('result')
    # print('\n\n kitchen id:' + str(id) + '\n\n')
    #
    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%d')
    todays_datetime = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')

    # allMeals = db.scan(
    #     TableName='meals',
    #     FilterExpression='kitchen_id = :val',
    #     ExpressionAttributeValues={
    #         ':val': {'S': login_session['user_id']},
    #     }
    # )

    meals = {}
    previousMeals = {}
    mealItems = []
    previousMealsItems = []

    # Close the business if 0 meals
    if allMeals == []:
        db.update_item(TableName='kitchens',
            Key={'kitchen_id': {'S': str(kitchen_id)}},
            UpdateExpression='SET isOpen = :val',
            ExpressionAttributeValues={
                ':val': {'BOOL': False}
            }
        )
        print("set isOpen to false")

    for meal in allMeals:
        twelveHourTime = datetime.strptime(meal['created_at']['S'][11:16], '%H:%M')
        meal['order_time'] = twelveHourTime.strftime('%I:%M %p')
        meal['price']['S'] = locale.currency(float(meal['price']['S']))[1:]
        if todays_date in meal['created_at']['S'] or meal['auto_renew']['BOOL']:
            mealItems.append(meal)
        else:
            previousMealsItems.append(meal)

    meals['Items'] = sorted(mealItems, key=itemgetter('order_time'), reverse=True)
    previousMeals['Items'] = sorted(previousMealsItems, key=itemgetter('order_time'), reverse=True)

    # print('\n\n' + str(meals) + '\n\n')
    # print('\n\n' + str(previousMeals) + '\n\n')

    todaysMenu = meals['Items']
    pastMenu = previousMeals['Items']
    #
    # print('\n\n' + str(meals) + '\n\n')
    # print('\n\n' + str(previousMeals) + '\n\n')
    #
    # todaysMenu = allMeals['Items']
    # pastMenu = previousMeals['Items']


    if todaysMenu == None:
      todaysMenu = []

    kitchen = db.scan(TableName='kitchens',
                      FilterExpression='kitchen_id = :value',
                      ExpressionAttributeValues={
                          ':value': {'S': current_user.get_id()},
                      }
    )

    description = kitchen['Items'][0]['description']['S']
    kitchenImage = kitchen['Items'][0]['kitchen_image']['S']


    return render_template('kitchen.html',
                            description=description,
                            kitchenName=login_session['kitchen_name'],
                            kitchenImage=kitchenImage,
                            id=login_session['user_id'],
                            todaysMeals=todaysMenu,
                            pastMenu = pastMenu
                            )


@app.route('/kitchens/<string:id>/settings', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
@login_required
def kitchenSettings(id):
    form = UpdateAccountForm()
    kitchen = db.scan(TableName='kitchens',
                      FilterExpression='kitchen_id = :value',
                      ExpressionAttributeValues={
                          ':value': {'S': current_user.get_id()},
                      }
    )['Items'][0]
    form.validate_on_submit()
    if form.validate_on_submit():
        delivery = False
        pickup = False
        disposable = False
        reusable = False
        canCancel = False
        if form.transport.data == 'delivery':
            delivery = True
        if form.transport.data == 'pickup':
            pickup = True
        if form.storage.data == 'disposable':
            disposable = True
        if form.storage.data == 'reusable':
            reusable = True
        if form.cancellation.data == 'canCancel':
            canCancel = True

        acceptingHours = [ {'M': {'is_accepting': {'BOOL':form.isAcceptingSunday.data},
                                  'open_time': {'S':form.acceptingOpenTimeSunday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeSunday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingMonday.data},
                                  'open_time': {'S':form.acceptingOpenTimeMonday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeMonday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingTuesday.data},
                                  'open_time': {'S':form.acceptingOpenTimeTuesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeTuesday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingWednesday.data},
                                  'open_time': {'S':form.acceptingOpenTimeWednesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeWednesday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingThursday.data},
                                  'open_time': {'S':form.acceptingOpenTimeThursday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeThursday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingFriday.data},
                                  'open_time': {'S':form.acceptingOpenTimeFriday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeFriday.data.strftime('%H:%M')}}},
                           {'M': {'is_accepting': {'BOOL':form.isAcceptingSaturday.data},
                                  'open_time': {'S':form.acceptingOpenTimeSaturday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.acceptingCloseTimeSaturday.data.strftime('%H:%M')}}}]

        deliveryHours =   [{'M': {'is_delivering': {'BOOL':form.isDeliveringSunday.data},
                                  'open_time': {'S':form.deliveryOpenTimeSunday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeSunday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringMonday.data},
                                  'open_time': {'S':form.deliveryOpenTimeMonday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeMonday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringTuesday.data},
                                  'open_time': {'S':form.deliveryOpenTimeTuesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeTuesday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringWednesday.data},
                                  'open_time': {'S':form.deliveryOpenTimeWednesday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeWednesday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringThursday.data},
                                  'open_time': {'S':form.deliveryOpenTimeThursday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeThursday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringFriday.data},
                                  'open_time': {'S':form.deliveryOpenTimeFriday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeFriday.data.strftime('%H:%M')}}},
                           {'M': {'is_delivering': {'BOOL':form.isDeliveringSaturday.data},
                                  'open_time': {'S':form.deliveryOpenTimeSaturday.data.strftime('%H:%M')},
                                  'close_time': {'S':form.deliveryCloseTimeSaturday.data.strftime('%H:%M')}}}]

        photoPath = kitchen['kitchen_image']['S']
        print('form.kitchenImage.data: ' + str(form.kitchenImage.data))
        if form.kitchenImage.data:
            kitchen_id = login_session['user_id']
            photo_key = 'kitchen_imgs/{}'.format(str(kitchen_id))
            delete_s3_img(BUCKET_NAME, photo_key)
            photoPath = upload_s3_img(form.kitchenImage.data, BUCKET_NAME, photo_key)

        db.update_item(TableName='kitchens',
                       Key={'kitchen_id': {'S': id}},
                       UpdateExpression='SET accepting_hours = :ah, \
                                             is_accepting_24hr = :a24, \
                                             can_cancel = :cc, \
                                             city = :c, \
                                             close_time = :ct, \
                                             delivery = :d, \
                                             delivery_hours = :dh, \
                                             delivery_close_time = :dct, \
                                             delivery_open_time = :dot, \
                                             description = :des, \
                                             disposable = :dis, \
                                             email = :e, \
                                             first_name = :fn, \
                                             kitchen_image = :ki, \
                                             kitchen_name = :kn, \
                                             last_name = :ln, \
                                             open_time = :ot, \
                                             phone_number = :pn, \
                                             pickup = :pi, \
                                             reusable = :r, \
                                             st = :st, \
                                             street = :s, \
                                             zipcode = :z',
                       ExpressionAttributeValues={
                           ':ah': {'L': acceptingHours},
                           ':a24': {'BOOL': form.isAccepting24hr.data},
                           ':cc': {'BOOL': canCancel},
                           ':c': {'S': form.city.data},
                           ':ct': {'S': form.acceptingCloseTimeMonday.data.strftime('%H:%M')},
                           ':d': {'BOOL': delivery},
                           ':dct': {'S': form.deliveryCloseTimeMonday.data.strftime('%H:%M')},
                           ':dot': {'S': form.deliveryOpenTimeMonday.data.strftime('%H:%M')},
                           ':dh': {'L': deliveryHours},
                           ':des': {'S': form.description.data},
                           ':dis': {'BOOL': disposable},
                           ':e': {'S':form.email.data.lower()},
                           ':fn': {'S': form.firstName.data},
                           ':ki': {'S': photoPath},
                           ':kn': {'S': form.kitchenName.data},
                           ':ln': {'S': form.lastName.data},
                           ':ot': {'S': form.acceptingOpenTimeMonday.data.strftime('%H:%M')},
                           # ':p': {'S': generate_password_hash(form.password.data)},
                           ':pn': {'S': form.phoneNumber.data},
                           ':pi': {'BOOL': pickup},
                           ':r': {'BOOL': reusable},
                           ':st': {'S': form.state.data},
                           ':s': {'S': form.street.data},
                           ':z': {'S': form.zipcode.data},
                       }
                       )

        login_session['kitchen_name'] = form.kitchenName.data
        login_session['email'] = form.email.data.lower()

        print(login_session['kitchen_name'])
        print(form.kitchenName.data)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('kitchenSettings', id=current_user.get_id()))
    elif request.method == 'GET':
        form.kitchenName.data = kitchen['kitchen_name']['S']
        form.description.data = kitchen['description']['S']
        if kitchen['delivery']['BOOL']:
            form.transport.data = 'delivery'
        else:
            form.transport.data = 'pickup'
        if kitchen['disposable']['BOOL']:
            form.storage.data = 'disposable'
        else:
            form.storage.data = 'reusable'
        if kitchen['can_cancel']['BOOL']:
            form.cancellation.data = 'canCancel'
        else:
            form.cancellation.data = 'cannotCancel'
        form.isAccepting24hr.data = kitchen['is_accepting_24hr']['BOOL']
        form.isAcceptingMonday.data = kitchen['accepting_hours']['L'][1]['M']['is_accepting']['BOOL']
        form.isAcceptingTuesday.data = kitchen['accepting_hours']['L'][2]['M']['is_accepting']['BOOL']
        form.isAcceptingWednesday.data = kitchen['accepting_hours']['L'][3]['M']['is_accepting']['BOOL']
        form.isAcceptingThursday.data = kitchen['accepting_hours']['L'][4]['M']['is_accepting']['BOOL']
        form.isAcceptingFriday.data = kitchen['accepting_hours']['L'][5]['M']['is_accepting']['BOOL']
        form.isAcceptingSaturday.data = kitchen['accepting_hours']['L'][6]['M']['is_accepting']['BOOL']
        form.isAcceptingSunday.data = kitchen['accepting_hours']['L'][0]['M']['is_accepting']['BOOL']
        form.acceptingOpenTimeMonday.data = datetime.strptime(kitchen['accepting_hours']['L'][1]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeTuesday.data = datetime.strptime(kitchen['accepting_hours']['L'][2]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeWednesday.data = datetime.strptime(kitchen['accepting_hours']['L'][3]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeThursday.data = datetime.strptime(kitchen['accepting_hours']['L'][4]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeFriday.data = datetime.strptime(kitchen['accepting_hours']['L'][5]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeSaturday.data = datetime.strptime(kitchen['accepting_hours']['L'][6]['M']['open_time']['S'], '%H:%M')
        form.acceptingOpenTimeSunday.data = datetime.strptime(kitchen['accepting_hours']['L'][0]['M']['open_time']['S'], '%H:%M')
        form.acceptingCloseTimeMonday.data = datetime.strptime(kitchen['accepting_hours']['L'][1]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeTuesday.data = datetime.strptime(kitchen['accepting_hours']['L'][2]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeWednesday.data = datetime.strptime(kitchen['accepting_hours']['L'][3]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeThursday.data = datetime.strptime(kitchen['accepting_hours']['L'][4]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeFriday.data = datetime.strptime(kitchen['accepting_hours']['L'][5]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeSaturday.data = datetime.strptime(kitchen['accepting_hours']['L'][6]['M']['close_time']['S'], '%H:%M')
        form.acceptingCloseTimeSunday.data = datetime.strptime(kitchen['accepting_hours']['L'][0]['M']['close_time']['S'], '%H:%M')
        form.isDeliveringSunday.data = kitchen['delivery_hours']['L'][0]['M']['is_delivering']['BOOL']
        form.isDeliveringMonday.data = kitchen['delivery_hours']['L'][1]['M']['is_delivering']['BOOL']
        form.isDeliveringTuesday.data = kitchen['delivery_hours']['L'][2]['M']['is_delivering']['BOOL']
        form.isDeliveringWednesday.data = kitchen['delivery_hours']['L'][3]['M']['is_delivering']['BOOL']
        form.isDeliveringThursday.data = kitchen['delivery_hours']['L'][4]['M']['is_delivering']['BOOL']
        form.isDeliveringFriday.data = kitchen['delivery_hours']['L'][5]['M']['is_delivering']['BOOL']
        form.isDeliveringSaturday.data = kitchen['delivery_hours']['L'][6]['M']['is_delivering']['BOOL']
        form.deliveryOpenTimeMonday.data = datetime.strptime(kitchen['delivery_hours']['L'][1]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeTuesday.data = datetime.strptime(kitchen['delivery_hours']['L'][2]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeWednesday.data = datetime.strptime(kitchen['delivery_hours']['L'][3]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeThursday.data = datetime.strptime(kitchen['delivery_hours']['L'][4]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeFriday.data = datetime.strptime(kitchen['delivery_hours']['L'][5]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeSaturday.data = datetime.strptime(kitchen['delivery_hours']['L'][6]['M']['open_time']['S'], '%H:%M')
        form.deliveryOpenTimeSunday.data = datetime.strptime(kitchen['delivery_hours']['L'][0]['M']['open_time']['S'], '%H:%M')
        form.deliveryCloseTimeMonday.data = datetime.strptime(kitchen['delivery_hours']['L'][1]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeTuesday.data = datetime.strptime(kitchen['delivery_hours']['L'][2]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeWednesday.data = datetime.strptime(kitchen['delivery_hours']['L'][3]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeThursday.data = datetime.strptime(kitchen['delivery_hours']['L'][4]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeFriday.data = datetime.strptime(kitchen['delivery_hours']['L'][5]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeSaturday.data = datetime.strptime(kitchen['delivery_hours']['L'][6]['M']['close_time']['S'], '%H:%M')
        form.deliveryCloseTimeSunday.data = datetime.strptime(kitchen['delivery_hours']['L'][0]['M']['close_time']['S'], '%H:%M')
        form.email.data = kitchen['email']['S']
        form.firstName.data = kitchen['first_name']['S']
        form.lastName.data = kitchen['last_name']['S']
        form.phoneNumber.data = kitchen['phone_number']['S']
        form.zipcode.data = kitchen['zipcode']['S']
        form.state.data = kitchen['st']['S']
        form.city.data = kitchen['city']['S']
        form.street.data = kitchen['street']['S']

    return render_template('kitchenSettings.html', form=form, id=id, kitchenName=login_session['kitchen_name'])


@app.route('/kitchens/meals/create', methods=['POST'])
@login_required
def postMeal():
    name = request.form.get('name')
    price = request.form.get('price')
    photo = request.files.get('photo')
    itemsData = request.form.get('items')

    if name == None or price == None or photo == None or itemsData == None:
        print('Meal details missing')
        return

    kitchen_id = current_user.get_id()

    meal_id = uuid.uuid4().hex
    created_at = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')

    meal_items = json.loads(itemsData)

    items = []
    for i in meal_items['meal_items']:
        item = {}
        item['title'] = {}
        item['title']['S'] = i['title']
        item['qty'] = {}
        item['qty']['N'] = str(i['qty'])
        items.append(item)

    description = [{'M': i} for i in items]

    print(description)

    # try:
    photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
    photoPath = upload_s3_img(photo, BUCKET_NAME, photo_key)

    if photoPath == None:
        raise BadRequest('Request failed. \
            Something went wrong uploading a photo.')

    add_meal = db.put_item(TableName='meals',
        Item={'meal_id': {'S': meal_id},
              'created_at': {'S': created_at},
              'kitchen_id': {'S': str(kitchen_id)},
              'meal_name': {'S': str(name)},
              'description': {'L': description},
              'price': {'S': str(price)},
              'photo': {'S': photoPath},
              'auto_renew': {'BOOL': False},
              'favorite': {'BOOL': False},
              'count_today': { 'N': '0' },
              'count_all': { 'N': '0' }
        }
    )

    kitchen = db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': str(kitchen_id)}},
        UpdateExpression='SET isOpen = :val',
        ExpressionAttributeValues={
            ':val': {'BOOL': True}
        }
    )

    print('Inside POST API')
    # print('kitchen:' + kitchen)
    # Technical debt that needs to be solved

    response['message'] = 'Request successful'
    return response, 200
    # except:
    #     raise BadRequest('Request failed. Please try again later.')

@app.route('/kitchens/meals/renew')
@login_required
def renewPastMeals():

    todays_datetime = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')

    allMeals = db.scan(
        TableName='meals',
        FilterExpression='kitchen_id = :val',
        ExpressionAttributeValues={
            ':val': {'S': login_session['user_id']},
        }
    )

    for meal in allMeals['Items']:

        renewedMeal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': str(meal['meal_id']['S'])}},
                                     UpdateExpression='SET created_at = :val',
                                     ExpressionAttributeValues={
                                        ':val': {'S':todays_datetime}}
                                     )

    return redirect(url_for('kitchen', id=login_session['user_id']))

@app.route('/kitchens/meals/renew/<id>')
@login_required
def renewIndvPastMeal(id):

    todays_datetime = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%dT%H:%M:%S')
    print (str(id))

    try:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': str(id)}},
                                     UpdateExpression='SET created_at = :ca, \
                                                           count_today = :ct',
                                     ExpressionAttributeValues={
                                         ':ca': {'S': todays_datetime},
                                         ':ct': {'N': '0'}

                                     }
                                     )
    except:
        flash('Meal not found.', 'danger')


    return redirect(url_for('kitchen', id=login_session['user_id']))


@app.route('/kitchens/meals/<string:meal_id>', methods=['POST'])
@login_required
def editMeal(meal_id):

    name = request.form.get('name')
    price = request.form.get('price')
    photo = request.files.get('photo')
    items_data = request.form.get('items')
    limit = request.form.get('limit')

    if name != None:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET meal_name = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': str(name)}
                                     }
                                     )

    if price != None:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET price = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': str(price)}
                                     }
                                     )

    if photo != None:
        photo_key = 'meals_imgs/{}_{}'.format(str(current_user.get_id()), str(meal_id))
        photoPath = upload_s3_img(photo, BUCKET_NAME, photo_key)

        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET photo = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': photoPath}
                                     }
                                     )

    if items_data != None:
        meal_items = json.loads(items_data)

        items = []
        for i in meal_items['meal_items']:
            item = {}
            item['title'] = {}
            item['title']['S'] = i['title']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            items.append(item)

        description = [{'M': i} for i in items]

        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET description = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'L': description}
                                     }
                                     )

@app.route('/adminreport/changestatus', methods=['PUT'])
def changeOrderStatus(meal_id):
    print("hey " + meal_id)

@app.route('/adminreport/<int:sort>')
@login_required
def adminreportFilter(sort):

    dataFilter = sort

    if 'kitchen_name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%d')

    orders = db.scan(
        TableName='meal_orders'
    )

    allMeals = db.scan(
        TableName='meals'
    )

    kitchen_names = db.scan(
        TableName="kitchens"
    )

    meals = {}
    previousMeals = {}
    mealItems = []
    previousMealsItems = []

    for meal in allMeals['Items']:
        mealItems.append(meal)

    meals['Items'] = mealItems
    previousMeals['Items'] = previousMealsItems

    todaysMenu = meals['Items']
    pastMenu = previousMeals['Items']

    if todaysMenu == None:
      todaysMenu = []

    totalRevenue = 0.0
    totalMealQuantity = {}
    for order in orders['Items']:
        for item in order['order_items']['L']:
            order_id = item['M']['meal_id']['S']
            order_id_str = str(order_id)

            meal = db.scan(TableName='meals',
                           FilterExpression='meal_id = :value',
                           ExpressionAttributeValues={
                               ':value': {'S':order_id
                               }
                           })

            if meal['Items']:
                mealInfo = meal['Items'][0]
                mealDescrip = mealInfo['description']['L'][0]['M']

                #print('\n\n' + str(item) + '\n\n')
                # TODO add meal specific price
                item['photo'] = mealInfo['photo']
                item['qty'] = int(item['M']['qty']['N'])
                item['revenue'] = float(mealInfo['price']['S']) * item['qty']
                item['price'] = locale.currency(float(mealInfo['price']['S']), grouping=True)
                totalRevenue += float(item['revenue'])
                #totalRevenue += item['revenue']
                item['revenue'] = locale.currency(item['revenue'], grouping=True)
                if order_id_str in totalMealQuantity:
                    totalMealQuantity[order_id_str] += item['qty']
                else:
                    totalMealQuantity[order_id_str] = item['qty']
                if item['qty'] > 0:
                  item['name'] = mealDescrip['title']['S']
                  update_meal = db.update_item(TableName='meals',
                                               Key={'meal_id': {'S': order_id}},
                                               UpdateExpression='SET count_today = :ct',
                                               ExpressionAttributeValues={
                                                   ':ct': {'N': str(totalMealQuantity[order_id_str])},
                                               }
                                               )

        twelveHourTime = datetime.strptime(order['created_at']['S'][11:16], '%H:%M')

    for order in orders['Items']:
        for kitchen in kitchen_names['Items']:
            if kitchen['kitchen_id']['S'] == order['kitchen_id']['S']:
                order['kitchen_id']['S'] = kitchen['kitchen_name']['S']

    if dataFilter == 1:
        sortedOrders = sorted(orders['Items'], key=lambda x: x['kitchen_id']['S'])
    elif dataFilter == 2:
        sortedOrders = sorted(orders['Items'], key=lambda x: x['kitchen_id']['S'])
    elif dataFilter == 3:
        sortedOrders = sorted(orders['Items'], key=lambda x: x['name']['S'])
    else:
        sortedOrders = sorted(orders['Items'], key=lambda x: datetime.strptime(x['created_at']['S'], '%Y-%m-%dT%H:%M:%S'), reverse=True)

    for order in sortedOrders:
        order['order_time'] = datetime.strptime(order['created_at']['S'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y %I:%M:%S%p')

    return render_template('adminreport.html',
                            kitchenName=login_session['kitchen_name'],
                            id=login_session['user_id'],
                            orders=sortedOrders,
                            totalRevenue = locale.currency(totalRevenue),
                            #todaysMeals = todaysMenu)
                            totalMealQuantity = totalMealQuantity)

@app.route('/adminreport')
@login_required
def adminreport():
    # update order to opened or closed
    # make this a button that can update an order in the database which lies within the container for each order
    # specify which farmer to which order
    # use kitchens database to get name of farmer using kitchen_id
    # sort orders based on farmerByItem, farmerByCustomer, and customerByItem

    if 'kitchen_name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%d')

    orders = db.scan(
        TableName='meal_orders'
    )

    allMeals = db.scan(
        TableName='meals'
    )

    kitchen_names = db.scan(
        TableName="kitchens"
    )

    meals = {}
    previousMeals = {}
    mealItems = []
    previousMealsItems = []

    for meal in allMeals['Items']:
        mealItems.append(meal)

    meals['Items'] = mealItems
    previousMeals['Items'] = previousMealsItems

    todaysMenu = meals['Items']
    pastMenu = previousMeals['Items']

    if todaysMenu == None:
      todaysMenu = []

    totalRevenue = 0.0
    totalMealQuantity = {}
    for order in orders['Items']:
        for item in order['order_items']['L']:
            order_id = item['M']['meal_id']['S']
            order_id_str = str(order_id)

            meal = db.scan(TableName='meals',
                           FilterExpression='meal_id = :value',
                           ExpressionAttributeValues={
                               ':value': {'S':order_id
                               }
                           })

            if meal['Items']:
                mealInfo = meal['Items'][0]
                mealDescrip = mealInfo['description']['L'][0]['M']

                #print('\n\n' + str(item) + '\n\n')
                # TODO add meal specific price
                item['photo'] = mealInfo['photo']
                item['qty'] = int(item['M']['qty']['N'])
                item['revenue'] = float(mealInfo['price']['S']) * item['qty']
                item['price'] = locale.currency(float(mealInfo['price']['S']), grouping=True)
                totalRevenue += float(item['revenue'])
                #totalRevenue += item['revenue']
                item['revenue'] = locale.currency(item['revenue'], grouping=True)
                if order_id_str in totalMealQuantity:
                    totalMealQuantity[order_id_str] += item['qty']
                else:
                    totalMealQuantity[order_id_str] = item['qty']
                if item['qty'] > 0:
                  item['name'] = mealDescrip['title']['S']
                  update_meal = db.update_item(TableName='meals',
                                               Key={'meal_id': {'S': order_id}},
                                               UpdateExpression='SET count_today = :ct',
                                               ExpressionAttributeValues={
                                                   ':ct': {'N': str(totalMealQuantity[order_id_str])},
                                               }
                                               )

        twelveHourTime = datetime.strptime(order['created_at']['S'][11:16], '%H:%M')

    sortedOrders = sorted(orders['Items'], key=lambda x: datetime.strptime(x['created_at']['S'], '%Y-%m-%dT%H:%M:%S'), reverse=True)

    for order in sortedOrders:
        order['order_time'] = datetime.strptime(order['created_at']['S'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y %I:%M:%S%p')
        for kitchen in kitchen_names['Items']:
            if kitchen['kitchen_id']['S'] == order['kitchen_id']['S']:
                order['kitchen_id']['S'] = kitchen['kitchen_name']['S']
        print(order['kitchen_id']['S'], file=sys.stderr)


        # order['created_at'] =

    # print(str(orders) + '\n\n')


    return render_template('adminreport.html',
                            kitchenName=login_session['kitchen_name'],
                            id=login_session['user_id'],
                            orders=sortedOrders,
                            totalRevenue = locale.currency(totalRevenue),
                            #todaysMeals = todaysMenu)
                            totalMealQuantity = totalMealQuantity)

@app.route('/kitchens/report')
@login_required
def report():
    if 'kitchen_name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime('%Y-%m-%d')

    orders = db.scan(TableName='meal_orders',
        FilterExpression='kitchen_id = :value',
        ExpressionAttributeValues={
            ':value': {'S': current_user.get_id()}
        }
    )

    allMeals = db.scan(
        TableName='meals',
        FilterExpression='kitchen_id = :val',
        ExpressionAttributeValues={
            ':val': {'S': login_session['user_id']},
        }
    )

    meals = {}
    previousMeals = {}
    mealItems = []
    previousMealsItems = []

    for meal in allMeals['Items']:
        mealItems.append(meal)

    meals['Items'] = mealItems
    previousMeals['Items'] = previousMealsItems

    todaysMenu = meals['Items']
    pastMenu = previousMeals['Items']

    if todaysMenu == None:
      todaysMenu = []

    totalPotentialRevenue = 0.0
    totalDeliveredRevenue = 0.0
    totalPotentialQuantity = {}
    totalDeliveredQuantity = {}
    for order in orders['Items']:
        for item in order['order_items']['L']:
            order_id = item['M']['meal_id']['S']
            order_id_str = str(order_id)

            meal = db.scan(TableName='meals',
                           FilterExpression='meal_id = :value',
                           ExpressionAttributeValues={
                               ':value': {'S':order_id
                               }
                           })

            if meal['Items']:
                mealInfo = meal['Items'][0]
                mealDescrip = mealInfo['description']['L'][0]['M']

                #print('\n\n' + str(item) + '\n\n')
                # TODO add meal specific price
                item['photo'] = mealInfo['photo']
                item['qty'] = int(item['M']['qty']['N'])
                item['revenue'] = float(mealInfo['price']['S']) * item['qty']
                item['price'] = locale.currency(float(mealInfo['price']['S']), grouping=True)
                if order['status']['S'] == 'open':
                    totalPotentialRevenue += float(item['revenue'])
                if order['status']['S'] == 'delivered':
                    totalDeliveredRevenue += float(item['revenue'])
                #totalRevenue += item['revenue']
                item['revenue'] = locale.currency(item['revenue'], grouping=True)
                if order['status']['S'] == 'open' and item['qty'] > 0:
                    if order_id_str in totalPotentialQuantity:
                        totalPotentialQuantity[order_id_str] += item['qty']
                    else:
                        totalPotentialQuantity[order_id_str] = item['qty']
                    item['name'] = mealInfo['meal_name']['S']
                if order['status']['S'] == 'delivered':
                    if order_id_str in totalDeliveredQuantity:
                        totalDeliveredQuantity[order_id_str] += item['qty']
                    else:
                        totalDeliveredQuantity[order_id_str] = item['qty']
                    if item['qty'] > 0:
                        item['name'] = mealInfo['meal_name']['S']
                    update_meal = db.update_item(TableName='meals',
                                                 Key={'meal_id': {'S': order_id}},
                                                 UpdateExpression='SET count_today = :ct',
                                                 ExpressionAttributeValues={
                                                     ':ct': {'N': str(totalDeliveredQuantity[order_id_str])},
                                                     }
                                                )
                print(item)

        twelveHourTime = datetime.strptime(order['created_at']['S'][11:16], '%H:%M')

    sortedOrders = sorted(orders['Items'], key=lambda x: datetime.strptime(x['created_at']['S'], '%Y-%m-%dT%H:%M:%S'), reverse=True)

    openOrders = []
    deliveredOrders = []
    for order in sortedOrders:
        order['order_time'] = datetime.strptime(order['created_at']['S'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y %I:%M:%S%p')
        if order['status']['S'] == 'open':
            openOrders.append(order)
        if order['status']['S'] == 'delivered':
            deliveredOrders.append(order)

    return render_template('report.html',
                            kitchenName=login_session['kitchen_name'],
                            id=login_session['user_id'],
                            openOrders=openOrders,
                            deliveredOrders=deliveredOrders,
                            totalPotentialRevenue = locale.currency(totalPotentialRevenue),
                            totalDeliveredRevenue = locale.currency(totalDeliveredRevenue),
                            todaysMeals = todaysMenu,
                            totalPotentialQuantity = totalPotentialQuantity,
                            totalDeliveredQuantity = totalDeliveredQuantity,
                            )


def closeKitchen(kitchen_id):
    closeKitchen = db.update_item(TableName='kitchens',
        Key={'kitchen_id': {'S': kitchen_id}},
        UpdateExpression='SET isOpen = :val',
        ExpressionAttributeValues={
            ':val': {'BOOL': False}
        }
    )

@app.route('/kitchens/hours')
def updateKitchensStatus():
    if request.headers['X-Appengine-Cron'] == 'true':
        currentTime = datetime.now(tz=timezone('US/Pacific')).strftime('%H:%M')

        kitchens = db.scan(TableName='kitchens')
        for kitchen in kitchens['Items']:
            closeTime = kitchen['close_time']['S']
            if kitchen['isOpen']['BOOL'] == True:
                if currentTime.rsplit(':', 1)[0] == closeTime.rsplit(':', 1)[0]:
                    if int(currentTime.rsplit(':', 1)[1]) > int(closeTime.rsplit(':', 1)[1]):
                        closeKitchen(kitchen['kitchen_id']['S'])
                elif int(currentTime.rsplit(':', 1)[0]) > int(closeTime.rsplit(':', 1)[0]):
                    closeKitchen(kitchen['kitchen_id']['S'])
        return 'testing cron jobs'


@app.route('/api/v1/meals/<meal_id>', methods=['GET', 'PUT'])
def delete(meal_id):
    # flash('meal id for the selected meal is {}'.format(meal_id))

    #input argument validation
    response = {}
    print('Inside delete..')
    print('meal_id', meal_id)

    try:
        #Get kitchen id and delete from s3 bucket first
        response = db.get_item(TableName='meals',Key={'meal_id':{'S':str(meal_id)}})

        kitchen_id = response['Item']['kitchen_id']['S']
        print('kitchen_id : ', kitchen_id)

        photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
        print('photo_key : ', photo_key)

        #delete from meals table
        deleted_meal = db.delete_item(TableName='meals',
                                      Key={'meal_id': {'S': meal_id}})

        delete_s3_img(BUCKET_NAME, photo_key)

        response['message'] = 'Request successful'
        return response, 200
    except Exception as ex:
        print('ex: ', ex)
        raise BadRequest('Request failed. Please try again later.')

@app.route('/api/v1/meals/auto_renew/<string:meal_id>')
def autoRenewMeal(meal_id):

    meal = db.scan(TableName='meals',
                   FilterExpression='meal_id = :value',
                   ExpressionAttributeValues={
                       ':value': {'S': meal_id},
                   }
    )

    old_auto_renew_val = meal['Items'][0]['auto_renew']['BOOL']
    new_auto_renew_val = not old_auto_renew_val

    auto_renew_meal = db.update_item(TableName='meals',
                              Key={'meal_id': {'S': str(meal_id)}},
                              UpdateExpression='SET auto_renew = :val',
                              ExpressionAttributeValues={
                                  ':val': {'BOOL':new_auto_renew_val}}
                              )
    return redirect(url_for('kitchen', id=login_session['user_id']))


@app.route('/api/v1/meals/fav/<string:meal_id>', methods=['POST'])
def favorite(meal_id):
    # flash('meal id for the selected meal is {}'.format(meal_id))

# input argument validation
    response = {}
    print('Inside favorite..')

    # get meal from meals table
    meal = db.scan(TableName='meals',
                   FilterExpression='meal_id = :value',
                   ExpressionAttributeValues={
                       ':value': {'S': meal_id},
                   }
    )

    old_fav_val = meal['Items'][0]['favorite']['BOOL']
    new_fav_val = not old_fav_val

    fav_meal = db.update_item(TableName='meals',
                              Key={'meal_id': {'S': str(meal_id)}},
                              UpdateExpression='SET favorite = :val',
                              ExpressionAttributeValues={
                                  ':val': {'BOOL':new_fav_val}}
                              )

    response['message'] = 'Request successful'
    return response, 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)
