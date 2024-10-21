from flask import render_template, Blueprint, redirect, url_for, flash, session, request, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt, os
from db import mysql
from functions import allowed_file
from werkzeug.utils import secure_filename
from datetime import datetime
import ast

api = Blueprint('api', __name__)
secret_key = os.urandom(24)

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


@api.route('/')
def home():
    return render_template("index.html")

@api.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO file_manager.users (username, email, password, created_at) VALUES (%s, %s, %s, NOW())', (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        flash("User registered successfully! Redirected to login...", "success")

        return redirect(url_for('api.login'))
    else:
        print("Form validation errors:", form.errors)

    return render_template("register.html", form=form)

@api.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM file_manager.users WHERE email=%s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            print(f"Stored Hash: {user[3]}")
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                    session['user_id'] = user[0]
                    return redirect(url_for('api.dashboard'))
            except ValueError as e:
                print(f"Error verifying password: {e}")
                flash("An error occurred while logging in. Please try again.", "danger")
                return redirect(url_for('api.login'))

        flash("Email or password is incorrect.", "danger")

    return render_template("login.html", form=form)

@api.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("SELECT * FROM file_manager.users WHERE id=%s", (user_id,))
            user = cursor.fetchone()

            if user:
                cursor.execute("SELECT * FROM file_manager.user_files WHERE user_id=%s", (user_id,))
                files = cursor.fetchall()
                
                return render_template("dashboard.html", user=user, files=files)
        finally:
            cursor.close()
    return redirect(url_for('login'))

@api.route('/upload', methods=['GET','POST'])
def upload_file():
    if 'user_id' in session:
        user_id = session['user_id']
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)

            # Save file metadata in the database
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO file_manager.user_files (user_id, file_name, file_path, file_size) VALUES (%s, %s, %s, %s)",
                           (user_id, filename, file_path, file_size,))
            mysql.connection.commit()
            cursor.close()

            flash("File uploaded successfully.", "success")
            return redirect(url_for('api.dashboard'))
    return redirect(url_for('api.dashboard'))

@api.route('/delete', methods=['POST'])
def delete_files():
    if 'user_id' in session:
        file_ids = request.form.getlist('files')
        cursor = mysql.connection.cursor()

        try:
            for file_id in file_ids:
                parts = file_id.strip().strip("()").split(", ")
                
                id_to_use = parts[0]
                cursor.execute("SELECT file_path FROM file_manager.user_files WHERE id=%s", (id_to_use,))
                file_record = cursor.fetchone()
                print("File record found:", file_record)  # Debugging line

                if file_record:
                    file_path = file_record[0]

                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        print(f"File does not exist: {file_path}")  # Debugging line
                    cursor.execute("DELETE FROM file_manager.user_files WHERE id=%s", (id_to_use,))
                    mysql.connection.commit()
                    print(f"Deleted record for file_id: {id_to_use}")
                else:
                    print(f"No record found for ID: {id_to_use}")  # Debugging line
            flash("Selected files deleted successfully.", "success")
        except Exception as e:
            flash("Error deleting files: " + str(e), "danger")
        finally:
            cursor.close()

    return redirect(url_for('api.dashboard'))

@api.route('/logout')
def logout():
    return render_template("logout.html")
# @api.route('/test-db-connection')
# def test_db_connection():
#     cursor = None  # Initialize cursor to None
#     try:
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT 1")  # Simple query to test connection
#         return "Database connection successful!"
#     except Exception as e:
#         return f"Error: {str(e)}"
#     finally:
#         if cursor:
#             cursor.close()  # Close the cursor if it was created

