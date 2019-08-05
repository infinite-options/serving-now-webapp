# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-05-24 19:40:12
# @Last Modified by:   Prashant Marathay
# @Last Modified time: 2019-07-26 19:10:31

import boto3
import json
import uuid
import requests

from datetime import datetime
from pytz import timezone

from flask import (Flask, Blueprint, request, render_template,
    redirect, url_for, flash)
from flask import session as login_session
from flask_login import (LoginManager, login_required, current_user,
	UserMixin, login_user, logout_user)
from flask_mail import Mail, Message
from flask_cors import CORS, cross_origin

from forms import RegistrationForm, LoginForm, UpdateAccountForm


from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import (generate_password_hash,
    check_password_hash)


app = Flask(__name__, static_folder='static', template_folder='templates')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, support_credentials=True)

login_manager = LoginManager(app)

secret_key = 'app_secret_key'

app.config['SECRET_KEY'] = secret_key
app.config['MAIL_USERNAME'] = 'infiniteoptions.meals@gmail.com'
app.config['MAIL_PASSWORD'] = 'annApurna'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

db = boto3.client('dynamodb')
s3 = boto3.client('s3')

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



# =======HELPER FUNCTIONS FOR UPLOADING AN IMAGE=============

def upload_meal_img(file, bucket, key):
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
    if str == 'false' or str == 'False':
        return False

def allowed_file(filename):
    """Checks if the file is allowed to upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =======HELPER FUNCTIONS FOR DELETING AN IMAGE=============

def delete_meal_img(bucket, key):
    print ("Inside delete_meal_img..")
    print ("bucket: ", bucket)
    print ("key: ", key)

    try:
        delete_file = s3.delete_object(
                            Bucket=bucket,
                            Key=key)
        print("delete_file : ", delete_file)

    except:
        print ("Item cannot be deleted")

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


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/accounts/logout')
@login_required
def logout():
    del login_session['user_id']
    del login_session['kitchen_name']
    logout_user()
    return redirect(url_for('index'))


@app.route('/accounts', methods=['GET', 'POST'])
@app.route('/accounts/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in login_session:
        return redirect(url_for('kitchen', id=login_session['user_id']))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Enter an email and password')
            return render_template('login.html')

        try:
            user = db.query(TableName="kitchens",
                IndexName='email-index',
                Limit=1,
                KeyConditionExpression='email = :val',
                ExpressionAttributeValues={
                    ':val': {'S': email}
                }
            )

            if user.get('Count') == 0:
                flash('User not found.')
                return render_template('login.html')

            if not check_password_hash(user['Items'][0]['password']['S'], \
              password):
                flash('Password is incorrect.')
                return render_template('login.html')
            else:
                user_id = user['Items'][0]['kitchen_id']['S']
                login_session['kitchen_name'] = user['Items'][0]['kitchen_name']['S']
                login_session['user_id'] = user_id
                login_session['email'] = user['Items'][0]['email']['S']
                login_session['username'] = user['Items'][0]['username']['S']
                login_user(User(user_id))
                return redirect(url_for('kitchen', id=user_id))

        except Exception as e:
            flash('Unable to connect to database.')
            print(e)
            return render_template('login.html')

    return render_template('login.html')


@app.route('/accounts/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RegistrationForm(request.form)
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

        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")
        kitchen_id = uuid.uuid4().hex
        add_kitchen = db.put_item(TableName='kitchens',
                    Item={'kitchen_id': {'S': kitchen_id},
                          'created_at': {'S': created_at},
                          'kitchen_name': {'S': form.kitchenName.data},
                          'description': {'S': form.description.data},
                          'username': {'S': form.username.data},
                          'password': {'S': generate_password_hash(form.password.data)},
                          'first_name': {'S': form.firstName.data},
                          'last_name': {'S': form.lastName.data},
                          'street': {'S': form.street.data},
                          'city': {'S': form.city.data},
                          'st': {'S': form.state.data},
                          'zipcode': {'N': form.zipcode.data},
                          'phone_number': {'S': form.phoneNumber.data},
                          'open_time': {'S': form.openTime.data.strftime('%H:%M')},
                          'close_time': {'S': form.closeTime.data.strftime('%H:%M')},
                          'isOpen': {'BOOL': False},
                          'email': {'S': form.email.data},
                          'delivery_open_time': { 'S': form.deliveryOpenTime.data.strftime('%H:%M')},
                          'delivery_close_time': { 'S': form.deliveryCloseTime.data.strftime('%H:%M')},
                          'delivery': { 'BOOL': delivery},
                          'pickup': { 'BOOL': pickup},
                          'disposable': { 'BOOL': disposable},
                          'reusable': { 'BOOL': reusable},
                          'can_cancel': { 'BOOL': canCancel }
                    }
                )
        flash('Your account has been created! You are now able to log in.', 'success') # python 3 format.
        print("Account for " + form.email.data + " has been created")
        return redirect(url_for('login'))

    print(form.errors)

    return render_template('register.html', title='Register', form=form) #  This is what happens if the submit is unsuccessful with errors highlighted

@app.route('/kitchens/<string:id>')
@login_required
def kitchen(id):
    # return render_template('kitchen.html')
    # if 'name' not in login_session:
    #     return redirect(url_for('index'))
    #
    apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    # apiURL = 'http://localhost:5000/api/v1/meals/' + current_user.get_id()

    # print("API URL: " + str(apiURL))
    # apiURL = API_BASE_URL + '/api/v1/meals/' + '5d114cb5c4f54c94a8bb4d955a576fca'
    response = requests.get(apiURL)
    #
    allMeals = response.json().get('result')
    # print("\n\n kitchen id:" + str(id) + "\n\n")
    #
    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

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

    for meal in allMeals:
        if todays_date in meal['created_at']['S']:
            mealItems.append(meal)
        else:
            previousMealsItems.append(meal)

    meals['Items'] = mealItems
    previousMeals['Items'] = previousMealsItems

    # print("\n\n" + str(meals) + "\n\n")
    # print("\n\n" + str(previousMeals) + "\n\n")

    todaysMenu = meals["Items"]
    pastMenu = previousMeals["Items"]
    #
    # print("\n\n" + str(meals) + "\n\n")
    # print("\n\n" + str(previousMeals) + "\n\n")
    #
    # todaysMenu = allMeals["Items"]
    # pastMenu = previousMeals["Items"]


    if todaysMenu == None:
      todaysMenu = []

    kitchen = db.scan(TableName='kitchens',
                      FilterExpression='kitchen_id = :value',
                      ExpressionAttributeValues={
                          ':value': {'S': current_user.get_id()},
                      }
    )

    description = kitchen['Items'][0]['description']['S']


    return render_template('kitchen.html',
                            description=description,
                            kitchen_name=login_session['kitchen_name'],
                            id=login_session['user_id'],
                            todaysMeals=todaysMenu,
                            pastMenu = pastMenu
                            )


@app.route('/kitchens/<string:id>/settings', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
@login_required
def kitchenSettings(id):
    form = UpdateAccountForm()
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
        db.update_item(TableName='kitchens',
                       Key={'kitchen_id': {'S': id}},
                       UpdateExpression='SET can_cancel = :cc, \
                                             city = :c, \
                                             close_time = :ct, \
                                             delivery = :d, \
                                             delivery_close_time = :dct, \
                                             delivery_open_time = :dot, \
                                             description = :des, \
                                             disposable = :dis, \
                                             email = :e, \
                                             first_name = :fn, \
                                             kitchen_name = :kn, \
                                             last_name = :ln, \
                                             open_time = :ot, \
                                             password = :p, \
                                             phone_number = :pn, \
                                             pickup = :pi, \
                                             reusable = :r, \
                                             st = :st, \
                                             street = :s, \
                                             username = :u, \
                                             zipcode = :z',
                       ExpressionAttributeValues={
                           ':cc': {'BOOL': canCancel},
                           ':c': {'S': form.city.data},
                           ':ct': {'S': form.closeTime.data.strftime('%H:%M')},
                           ':d': {'BOOL': delivery},
                           ':dct': {'S': form.deliveryCloseTime.data.strftime('%H:%M')},
                           ':dot': {'S': form.deliveryOpenTime.data.strftime('%H:%M')},
                           ':des': {'S': form.description.data},
                           ':dis': {'BOOL': disposable},
                           ':e': {'S':form.email.data},
                           ':fn': {'S': form.firstName.data},
                           ':kn': {'S': form.kitchenName.data},
                           ':ln': {'S': form.lastName.data},
                           ':ot': {'S': form.openTime.data.strftime('%H:%M')},
                           ':p': {'S': generate_password_hash(form.password.data)},
                           ':pn': {'S': form.phoneNumber.data},
                           ':pi': {'BOOL': pickup},
                           ':r': {'BOOL': reusable},
                           ':st': {'S': form.state.data},
                           ':s': {'S': form.street.data},
                           ':u': {'S': form.username.data},
                           ':z': {'S': form.zipcode.data},
                       }
                       )
        flash('Your account has been updated!', 'success')
        return redirect(url_for('kitchenSettings', id=current_user.get_id()))
    elif request.method == 'GET':
        kitchen = db.scan(TableName='kitchens',
                          FilterExpression='kitchen_id = :value',
                          ExpressionAttributeValues={
                              ':value': {'S': current_user.get_id()},
                          }
        )['Items'][0]

        form.kitchenName.data = kitchen['kitchen_name']['S']
        form.description.data = kitchen['description']['S']
        form.closeTime.data = datetime.strptime(kitchen['close_time']['S'], '%H:%M')
        form.openTime.data = datetime.strptime(kitchen['open_time']['S'], '%H:%M')
        form.deliveryOpenTime.data = datetime.strptime(kitchen['delivery_open_time']['S'], '%H:%M')
        form.deliveryCloseTime.data = datetime.strptime(kitchen['delivery_close_time']['S'], '%H:%M')
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
        form.username.data = kitchen['username']['S']
        form.email.data = kitchen['email']['S']
        form.firstName.data = kitchen['first_name']['S']
        form.lastName.data = kitchen['last_name']['S']
        form.phoneNumber.data = kitchen['phone_number']['S']
        form.zipcode.data = kitchen['zipcode']['S']
        form.state.data = kitchen['st']['S']
        form.city.data = kitchen['city']['S']
        form.street.data = kitchen['street']['S']

    return render_template('kitchenSettings.html', form=form, id=id, kitchen_name=login_session['kitchen_name'])


    # updates = {}
    #
    # print("\n\n"+ str(request.form.get('type')) +"\n\n")
    #
    # if request.form.get('type') == 'registration':
    #     updates["username"] = request.form.get('payload[username]')
    #     updates["password"] = generate_password_hash(request.form.get('payload[password]'))
    #
    # if request.form.get('type') == 'personal':
    #     updates["first_name"] = request.form.get('payload[first_name]')
    #     updates["last_name"] = request.form.get('payload[last_name]')
    #     updates["street"] = request.form.get('payload[street]')
    #     updates["city"] = request.form.get('payload[city]')
    #     updates["st"] = request.form.get('payload[state]')
    #     updates["zipcode"] = request.form.get('payload[zipcode]')
    #     updates["phone_number"] = request.form.get('payload[phone_number]')
    #     updates["email"] = request.form.get('payload[email]')
    #
    # if request.form.get('type') == 'kitchen':
    #     updates["kitchen_name"] = request.form.get('payload[kitchen_name]')
    #     updates["description"] = request.form.get('payload[description]')
    #     updates["open_time"] = request.form.get('payload[open_time]')
    #     updates["close_time"] = request.form.get('payload[close_time]')
    #     updates["delivery_open_time"] = request.form.get('payload[delivery_open_time]')
    #     updates["delivery_close_time"] = request.form.get('payload[delivery_close_time]')
    #     updates["delivery"] = strToBool(request.form.get('payload[delivery]'))
    #     updates["pickup"] = strToBool(request.form.get('payload[pickup]'))
    #     updates["reusable"] = strToBool(request.form.get('payload[reusable]'))
    #     updates["disposable"] = strToBool(request.form.get('payload[disposable]'))
    #     updates["can_cancel"] = strToBool(request.form.get('payload[cancellation_option]'))
    #
    # for field in updates:
    #
    #     print("\n\n\n"+ str(updates[field]) +"\n")
    #     print(str(field) +"\n")
    #
    #     if (updates[field]) == None:
    #         flash('Please fill ' + field + ' in')
    #     else:
    #         keyVal = {"":""}
    #
    #         if isinstance(updates[field], str):
    #             keyVal = {'S': updates[field]}
    #         elif isinstance(updates[field], bool):
    #             keyVal = {'BOOL': updates[field]}
    #         elif isinstance(updates[field], int):
    #             keyVal = {'N': updates[field]}
    #
    #         print(str(keyVal) +"\n\n\n")
    #
    #         update = db.update_item(TableName='kitchens',
    #                                  Key={'kitchen_id': {'S': id}},
    #                                  UpdateExpression='SET ' + field + ' = :n',
    #                                  ExpressionAttributeValues={
    #                                      ':n': keyVal
    #                                      }
    #                                 )
    #
    # kitchen = db.scan(TableName='kitchens',
    #                   FilterExpression='kitchen_id = :value',
    #                   ExpressionAttributeValues={
    #                       ':value': {'S': id}
    #                   })
    #
    # return render_template('kitchenSettings.html',
    #                         id=id,
    #                         kitchen=kitchen['Items'][0],
    #                         kitchen_name=login_session['kitchen_name'])


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
    created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

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
    photo_path = upload_meal_img(photo, BUCKET_NAME, photo_key)

    if photo_path == None:
        raise BadRequest('Request failed. \
            Something went wrong uploading a photo.')

    add_meal = db.put_item(TableName='meals',
        Item={'meal_id': {'S': meal_id},
              'created_at': {'S': created_at},
              'kitchen_id': {'S': str(kitchen_id)},
              'meal_name': {'S': str(name)},
              'description': {'L': description},
              'price': {'S': str(price)},
              'photo': {'S': photo_path},
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

    print("Inside POST API")
    # print("kitchen:" + kitchen)
    # Technical debt that needs to be solved

    response['message'] = 'Request successful'
    return response, 200
    # except:
    #     raise BadRequest('Request failed. Please try again later.')

@app.route('/kitchens/meals/renew')
@login_required
def renewPastMeals():

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

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
                                        ':val': {'S':todays_date}}
                                     )

    return redirect(url_for('kitchen', id=login_session['user_id']))

@app.route('/kitchens/meals/renew/<id>')
@login_required
def renewIndvPastMeal(id):

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

    try:
        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': str(id)[:-6]}},
                                     UpdateExpression='SET created_at = :val',
                                     ExpressionAttributeValues={
                                         ':val': {'S': todays_date}
                                     }
                                     )
    except:
        flash(f'Meal not found.', 'danger') # python 3 format.


    return redirect(url_for('kitchen', id=login_session['user_id']))


@app.route('/kitchens/meals/<string:meal_id>', methods=['POST'])
@login_required
def editMeal(meal_id):
    # print("edit meal api called: Server Side")
    # print(meal_id)
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
        photo_path = upload_meal_img(photo, BUCKET_NAME, photo_key)

        update_meal = db.update_item(TableName='meals',
                                     Key={'meal_id': {'S': meal_id}},
                                     UpdateExpression='SET photo = :n',
                                     ExpressionAttributeValues={
                                         ':n': {'S': photo_path}
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
    #
    # # TODO: if the limit was removed, update meal to remove the given limit
    # if limit != None:
    #     update_meal = db.update_item(TableName='meals',
    #                                  Key={'meal_id': {'S': meal_id}},
    #                                  UpdateExpression='SET #l = :l',
    #                                  ExpressionAttributeNames={
    #                                      '#l': 'limit'
    #                                  },
    #                                  ExpressionAttributeValues={
    #                                      ':n': {'N': str(limit)}
    #                                  }
    #                                  )

    # return redirect(url_for('kitchen', id="5d114cb5c4f54c94a8bb4d955a576fca"))
    # return redirect(url_for('kitchen', id=current_user.get_id()))


@app.route('/kitchens/report')
@login_required
def report():
    if 'kitchen_name' not in login_session:
        return redirect(url_for('index'))

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
    orders = db.scan(TableName='meal_orders',
        FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
        ExpressionAttributeValues={
            ':value': {'S': current_user.get_id()},
            ':x1': {'S': todays_date}
        }
    )

    todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

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
        if todays_date in meal['created_at']['S']:
            mealItems.append(meal)
        else:
            previousMealsItems.append(meal)

    meals['Items'] = mealItems
    previousMeals['Items'] = previousMealsItems

    # print("\n\n" + str(meals) + "\n\n")
    # print("\n\n" + str(previousMeals) + "\n\n")

    todaysMenu = meals["Items"]
    pastMenu = previousMeals["Items"]

    # todaysMenu = db.Table('meals')
    if todaysMenu == None:
      todaysMenu = []

    # apiURL = API_BASE_URL +'/api/v1/meals/' + current_user.get_id()
    # response = requests.get(apiURL)
    #
    # todaysMenu = response.json().get('result')
    # mealsToCook = todaysMenu

    # for item in mealsToCook:
    #     item['qty'] = 0

    # meal
    #{'Items': [{'photo': {'S': 'https://s3-us-west-1.amazonaws.com/ordermealapp/meals_imgs/638ade3aaef0488f835aa0fb1a75d654_4b9a70fc5f194c7f93a3d5f65c11f9ff'}, 'created_at': {'S': '2019-07-18T13:49:40'}, 'kitchen_id': {'S': '638ade3aaef0488f835aa0fb1a75d654'}, 'favorite': {'BOOL': False}, 'price': {'S': '18'}, 'description': {'L': [{'M': {'title': {'S': 'Mac & Cheese'}, 'qty': {'N': '1'}}}]}, 'meal_id': {'S': '4b9a70fc5f194c7f93a3d5f65c11f9ff'}, 'meal_name': {'S': 'Vegan Mac & Cheese'}}], 'Count': 1, 'ScannedCount': 126, 'ResponseMetadata': {'RequestId': '4HD5TCV1TGS94UG3R8QEBBN2VVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu, 18 Jul 2019 21:35:24 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '488', 'connection': 'keep-alive', 'x-amzn-requestid': '4HD5TCV1TGS94UG3R8QEBBN2VVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3635124217'}, 'RetryAttempts': 0}}

    # orders
#     {'created_at': {'S': '2019-07-18T13:58:53'}, 'kitchen_id': {'S': '638ade3aaef0488f835aa0fb1a75d654'}, 'totalAmount': {'N': '113.36'}, 'email': {'S': 'Jeremy.h.manalo@gmail.com'}, 'order_items': {'L': [{'M': {'meal_id': {'S': '4b9a70fc5f194c7f93a3d5f65c11f9ff'}, 'qty': {'N': '2'}}, 'photo': {'S': 'https://s3-us-west-1.amazonaws.com/ordermealapp/meals_imgs/638ade3aaef0488f835aa0fb1a75d654_4b9a70fc5f194c7f93a3d5f65c11f9ff'}, 'qty': 1, 'meal_name': 'Mac & Cheese'}, {'M': {'meal_id': {'S': '86286f2ad0ac44cab39c8262a8120e72'}, 'qty': {'N': '4'}}, 'photo': {'S': 'https://s3-us-west-1.amazonaws.com/ordermealapp/meals_imgs/638ade3aaef0488f835aa0fb1a75d654_86286f2ad0ac44cab39c8262a8120e72'}, 'qty': 2, 'meal_name': 'bread'}, {'M': {'meal_id': {'S': 'c641a125b3a3409b9348c819fa9e11c1'}, 'qty': {'N': '8'}}}]}, 'name': {'S': 'Jeremy Manalo'}, 'paid': {'BOOL': False}, 'state': {'S': 'CA'}, 'city': {'S': 'Santa Cruz'}, 'order_id': {'S': 'be5c293f2a9a4d3da8c6ce38c06d31ba'}, 'zipCode': {'N': '95060'}, 'phone': {'S': '8587767843'}, 'paymentType': {'S': 'cash'}, 'street': {'S': '434 Western Drive'}}

                # print("\n\n\nmeal: \n\n" + str(meal))


    totalRevenue = 0.0;
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

                #print("\n\n" + str(item) + "\n\n")
                # TODO add meal specific price
                item['photo'] = mealInfo['photo']
                item['qty'] = int(item['M']['qty']['N'])
                item['revenue'] = int(mealInfo['price']['S']) * item['qty']
                item['price'] = int(mealInfo['price']['S'])
                totalRevenue += float(item['revenue'])
                #totalRevenue += item['revenue']
                if order_id_str in totalMealQuantity:
                    totalMealQuantity[order_id_str] += item['qty']
                else:
                    totalMealQuantity[order_id_str] = item['qty']
                if item['qty'] > 0:
                  item['name'] = mealDescrip['title']['S']
                  update_meal = db.update_item(TableName='meals',
                                               Key={'meal_id': {'S': order_id}},
                                               UpdateExpression='SET count_today = :n',
                                               ExpressionAttributeValues={
                                                   ':n': {'N': str(totalMealQuantity[order_id_str])}
                                               }
                                               )
        order['created_at']['S'] = order['created_at']['S'][11:16]



        # order['created_at'] =

    # print(str(orders) + "\n\n")


    return render_template('report.html',
                            kitchen_name=login_session['kitchen_name'],
                            id=login_session['user_id'],
                            orders=orders['Items'],
                            totalRevenue = totalRevenue,
                            todaysMeals = todaysMenu,
                            totalMealQuantity = totalMealQuantity)


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
    print("Inside delete..")
    print("meal_id", meal_id)

    try:
        #Get kitchen id and delete from s3 bucket first
        response = db.get_item(TableName='meals',Key={'meal_id':{'S':str(meal_id)}})

        kitchen_id = response['Item']['kitchen_id']['S']
        print("kitchen_id : ", kitchen_id)

        photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
        print("photo_key : ", photo_key)

        #delete from meals table
        deleted_meal = db.delete_item(TableName='meals',
                                      Key={'meal_id': {'S': meal_id}}),

        delete_meal_img(BUCKET_NAME, photo_key)

        response['message'] = 'Request successful'
        return response, 200
    except Exception as ex:
        print("ex: ", ex)
        raise BadRequest('Request failed. Please try again later.')

# @app.route('/delete/meal/<string:meal_id>', methods=['GET', 'PUT'])
# def deleteMeal(meal_id):
#     flash('meal id for the selected meal is {}'.format(meal_id))
#
#     try:
#         deleted_meal = db.delete_item(TableName='meals',
#                        Key={'meal_id': {'S': meal_id}}),
#         #response['message'] = 'Request successful'
#         #return response, 200
#         return redirect(url_for('kitchen', id=current_user.get_id()))     # This seems to auto load the changes.  Can we use this everywhere?
#     except Exception as ex:
#         print("ex: ", ex)
#         raise BadRequest('Request failed. Please try again later.')
#     return redirect(url_for('kitchen', id=current_user.get_id()))


@app.route('/api/v1/meals/fav/<string:meal_id>', methods=['POST'])
def favorite(meal_id):
    # flash('meal id for the selected meal is {}'.format(meal_id))

# input argument validation
    response = {}
    print("Inside favorite..")

    # get meal from meals table
    meal = db.scan(TableName='meals',
                   FilterExpression='meal_id = :value',
                   ExpressionAttributeValues={
                       ':value': {'S': meal_id},
                   }
    )

    old_fav_val = meal['Items'][0]['favorite']['BOOL']
    new_fav_val = not old_fav_val
    #print(meal['Items'][0]['favorite']['BOOL'])
    # {'Items': [{'photo': {'S': 'https://s3-us-west-1.amazonaws.com/ordermealapp/meals_imgs/638ade3aaef0488f835aa0fb1a75d654_aa73e204e6ef4876affe53b447bc7c28'},'created_at': {'S': '2019-07-17T09:47:31'}, 'kitchen_id': {'S': '638ade3aaef0488f835aa0fb1a75d654'}, 'favorite': {'BOOL': False}, 'price': {'S': '100'}, 'description': {'L': [{'M': {'title': {'S': 'Test not order'}, 'qty': {'N': '1'}}}]}, 'meal_id': {'S': 'aa73e204e6ef4876affe53b447bc7c28'}, 'meal_name': {'S': 'Test not order'}}], 'Count': 1, 'ScannedCount': 113, 'ResponseMetadata': {'RequestId': 'J0P19HEM6J4QNE2NM2G2K6LC5RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 17 Jul 2019 18:14:24 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '487', 'connection': 'keep-alive', 'x-amzn-requestid': 'J0P19HEM6J4QNE2NM2G2K6LC5RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2345770100'}, 'RetryAttempts': 0}}


    fav_meal = db.update_item(TableName='meals',
                              Key={'meal_id': {'S': str(meal_id)}},
                              UpdateExpression='SET favorite = :val',
                              ExpressionAttributeValues={
                                  ':val': {'BOOL':new_fav_val}}
                              )

    response['message'] = 'Request successful'
    return response, 200
    #     #if isEnabled == True:
    #         fav_meal = db.update_item(TableName='meals',
    #                        Key={'ID': int(meal_id)},
    #                        UpdateExpression='SET isFavorite = :val',
    #                        ExpressionAttributeValues={
    #                            ':val': {'BOOL':True}
    #                        }
    #                        )
    #     #else:
    #         fav_meal = db.update_item(TableName='meals',
    #                        Key={'ID': int(meal_id)},
    #                        UpdateExpression='SET isFavorite = :val',
    #                        ExpressionAttributeValues={
    #                            ':val': {'BOOL': False}
    #                        }
    #                        )
       # response['message'] = 'Request successful'
       # return response, 200
    #except:
     #   raise BadRequest('Request failed. Please try again later.'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)
