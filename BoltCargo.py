from flask import Flask, render_template, request, redirect, url_for, g
import re
from twilio.rest import Client
from random import randint
import requests
import json
import ast
from validate_email import validate_email
import base64
# from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from flask_login import logout_user, login_user, LoginManager, UserMixin, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Amar/PycharmProjects/BoltCargo/login.db'
app.config['SECRET_KEY'] = 'boltcargo2019'
# es = Elasticsearch(hosts=[{'host': '142.93.209.45', 'port': 9200}])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mobile_sessions = {}
# account_sid = "AC183c725849f24c3eb29044c68742ad9a"

# auth_token = "3845f02ba8f6bfaabd15b5104c26f27e"

# client = Client(account_sid, auth_token)
mobile_number = ''


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


@app.route('/login', methods=['POST', 'GET'])
def login():
    global mobile_sessions
    message = {}
    global mobile_number
    if request.method == 'POST':
        # mobile_number = request.form.get('number')
        email_id = request.form.get('email')
        password = request.form.get('password')
        if (email_id is not None and password is not None):
            # rule = re.match("^[789]\d{9}$", mobile_number)
            valid_email = validate_email(email=email_id)
            if valid_email and len(password) > 6:
                user = UserModel.query.filter_by(email=email_id).first()
                if user is None:
                    message = {"status": "false", "message": "Invalid Email Id / Password."}
                    return render_template('login.html', message=message)

                login_user(user=user)
                return redirect(url_for('details'))
                # number = random_with_N_digits(4)
                # print(number)
                #  mobile_sessions[mobile_number] = str(number)
                #  print("+91{mobile}".format(mobile=mobile_number))
                #  message = client.messages.create(
                #      to="+91{mobile}".format(mobile=mobile_number),
                #       from_="+12082686450",
                #       body="Dear User, your one time password for BoltCargo login is {otp_number}".format(
                #           otp_number=number))
                return redirect(url_for('authenticate', messages=mobile_sessions))
            else:
                message = {"status": "false", "message": "Invalid Email Id / Password."}
        else:
            message = {'status': "intermediate"}

    return render_template('login.html', message=message)


@app.route('/register', methods=['POST', 'GET'])
def register():
    global mobile_sessions
    message = {}
    global mobile_number
    if request.method == 'POST':
        mobile_number = request.form.get('number')
        email_id = request.form.get('email')
        password = request.form.get('password')
        if (email_id is not None and password is not None):
            valid_email = validate_email(email=email_id)
            if valid_email == False:
                message = {"status": "false", "message": "Please enter valid email id."}
                return render_template('register.html', message=message)
            elif len(password) < 6:
                message = {"status": "false", "message": "Password should be 6 characters long."}
                return render_template('register.html', message=message)
            else:
                if valid_email and len(password) > 6:
                    user = UserModel.query.filter_by(email=email_id).first()
                    if user is not None:
                        message = {"status": "false", "message": "Email Id already exists."}
                        return render_template('register.html', message=message)

                    new_user = UserModel(email=email_id, password=password, mobile=mobile_number)

                    db.session.add(new_user)
                    db.session.commit()
                    # login_user(user=user)
                    return redirect(url_for('login'))

                    # return redirect(url_for('authenticate', messages=mobile_sessions))
                else:
                    message = {"status": "false", "message": "Invalid Email Id / Password."}
        else:
            message = {'status': "intermediate"}

    return render_template('register.html', message=message)


@app.route('/')
def hello_world():
    message = {'status': "intermediate"}
    return render_template('login.html', message=message)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    data = {}
    if request.method == 'POST':

        type = request.form.get('type')
        name = request.form.get('name')
        email = request.form.get('email')
        data = {'name': name, 'type': type, 'email': email}
        #print(data)
    return render_template('dashboard.html', message=data)


@app.route('/details', methods=['POST', 'GET'])
def details():
    message = {'status': "intermediate"}
    if request.method == 'POST':
        business_type = request.form.get('type')
        buisness_name = request.form.get('name')
        business_email = request.form.get('email')
        if (business_type is None or len(business_type) == 0):
            message = {"status": "false",
                       "message": "Enter your type of buisness: Shipper, Forwarder, Transporter, Admin"}
            return render_template('business_details.html', message=message)
        elif (buisness_name is None or len(buisness_name) == 0):
            message = {"status": "false",
                       "message": "Enter the name of your business"}
            return render_template('business_details.html', message=message)
        elif (business_email is None or len(business_email) == 0):
            message = {"status": "false",
                       "message": "Enter your business email"}
            return render_template('business_details.html', message=message)
        else:
            message = {"status": "true"}
            return render_template('business_details.html', message=message)

    return render_template('business_details.html', message=message)


@app.route('/authenticate', methods=['POST', 'GET'])
def authenticate():
    message = {}
    if request.method == 'POST':
        otp = request.form.get('number')

        if otp is not None:
            if mobile_sessions['9372464372'] == otp:
                return redirect(url_for('details'))
            else:
                message = {'message': 'Incorrect Otp', 'status': 'false'}
    return render_template('otp_auth.html', message=message)


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    mobile = db.Column(db.String(50))

# if __name__ == '__main__':
#    app.run()
