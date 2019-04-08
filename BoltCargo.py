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
from flask_login import logout_user, login_user, LoginManager, UserMixin, login_required, current_user
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Amar/PycharmProjects/BoltCargo/login.db'
app.config['SECRET_KEY'] = 'boltcargo2019'
# es = Elasticsearch(hosts=[{'host': '142.93.209.45', 'port': 9200}])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mobile_number = ''


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


# This route is used to login the user in the application
# Post successful login, the user is redirected to details page.
# If user is already authenticated, it is redirected to dashboard.
@app.route('/login', methods=['POST', 'GET'])
def login():
    message = {}
    global mobile_number
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':

        email_id = request.form.get('email')
        password = request.form.get('password')
        if (email_id is not None and password is not None):

            valid_email = validate_email(email=email_id)
            if valid_email and len(password) > 6:
                user = UserModel.query.filter_by(email=email_id).first()
                if user is None:
                    message = {"status": "false", "message": "Invalid Email Id / Password."}
                    return render_template('login.html', message=message)

                login_user(user=user)
                return redirect(url_for('details'))

            else:
                message = {"status": "false", "message": "Invalid Email Id / Password."}
        else:
            message = {'status': "intermediate"}

    return render_template('login.html', message=message)


# This route is used to register user in the application
# If user is already authenticated, the route will be redirected to dashboard
# Post succesful registration, the user reg. details are stored in database and redirected to details page
@app.route('/register', methods=['POST', 'GET'])
def register():
    message = {}
    global mobile_number

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

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
                    login_user(user=user)
                    return redirect(url_for('details'))

                else:
                    message = {"status": "false", "message": "Invalid Email Id / Password."}
        else:
            message = {'status': "intermediate"}

    return render_template('register.html', message=message)


# This is the index page of the application
# If user is already logged, it is redirected to the dashboard page
@app.route('/')
def hello_world():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    message = {'status': "intermediate"}
    return render_template('index.html', message=message)


# This is the dashboard page of the application
# This shows the user details and in future the more functionality will be added, like booking transporters etc
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    data = {}
    details = DetailsModels.query.filter_by(email=current_user.email).first()
    if (details is not None):
        data = {'name': details.business_name, 'type': details.user_type, 'email': details.email}
        return render_template('dashboard.html', message=data)
    if request.method == 'POST':
        type = request.form.get('type')
        name = request.form.get('name')
        email = request.form.get('email')
        conn = create_connection('C:/Users/Amar/PycharmProjects/BoltCargo/login.db')
        with conn:
            create_details(conn, (email, type, name))

        data = {'name': name, 'type': type, 'email': email}

    return render_template('dashboard.html', message=data)


# This is the details page of the application where the basic details are collected of the user
# The details filled here by the user are populated into dashboard page
# This route is important from business perspective
@app.route('/details', methods=['POST', 'GET'])
def details():
    message = {'status': "intermediate"}

    if request.method == 'POST':
        business_type = request.form.get('type')
        buisness_name = request.form.get('name')
        business_email = request.form.get('email')
        details = (business_email, business_type, buisness_name)
        details = DetailsModels.query.filter_by(email=current_user.email).first()
        if (details is None):
            conn = create_connection('C:/Users/Amar/PycharmProjects/BoltCargo/login.db')
            with conn:
                create_details(conn, details)

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


# Below route is not used currently
# Below route is useless for now
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


# The method generates 4 digit OTP.
# This was initially used for sending the OTP messages using Twilio.
# This method might be needed in future for sending the OTPs.
def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


# This is user model for login
# It stores the email id, password and mobile number of the user.
class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    mobile = db.Column(db.String(50))


# This is the details model. This schema is used by 'details' route for storing user details
# It stores business email, business type, and business name
class DetailsModels(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user_type = db.Column(db.String(100))
    business_name = db.Column(db.String(100))


# This method inserts the details of the user into database.
# It stores business email, business type, and business name from details page or dashboard page
def create_details(conn, details_model):
    sql = ''' INSERT INTO details_models(email,user_type,business_name)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, details_model)
    return cur.lastrowid


# This method creates the connection from app to the database.
# This is used for storing the details information of the user.
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None
