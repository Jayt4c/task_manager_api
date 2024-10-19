from flask import render_template, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_mysqldb import MySQL
import bcrypt


api = Blueprint('api', __name__)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

@api.route('/')
def index():
    return render_template("index.html")

@api.route('/register')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        #store registration data in database
        

    return render_template("register.html")

@api.route('/login', methods=['GET'])
def login():
    return render_template("login.html")

@api.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
    # from flask import Blueprint, request, jsonify
# from models import db, User, Task
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# api = Blueprint('api', __name__)

# @api.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     new_user = User(username=data['username'], password=data['password'])  # Hash password in production
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify(message="User created"), 201

# @api.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data['username']).first()
#     if user and user.password == data['password']:  # Hash comparison in production
#         access_token = create_access_token(identity=user.id)
#         return jsonify(access_token=access_token), 200
#     return jsonify(message="Bad username or password"), 401

# @api.route('/tasks', methods=['POST'])
# @jwt_required()
# def create_task():
#     data = request.get_json()
#     current_user = get_jwt_identity()
#     new_task = Task(title=data['title'], description=data['description'], user_id=current_user)
#     db.session.add(new_task)
#     db.session.commit()
#     return jsonify(new_task), 201

# @api.route('/tasks', methods=['GET'])
# @jwt_required()
# def get_tasks():
#     current_user = get_jwt_identity()
#     tasks = Task.query.filter_by(user_id=current_user).all()
#     return jsonify([task.serialize() for task in tasks]), 200  # Implement serialize method in Task model
