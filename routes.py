from flask import render_template, Blueprint, redirect, url_for, flash, session, request, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt, os
from db import mysql
from werkzeug.utils import secure_filename
from datetime import datetime

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

@app.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        try:
            # Fetch file metadata from the database
            cursor.execute("SELECT file_path FROM file_manager.user_files WHERE id=%s", (file_id,))
            file_record = cursor.fetchone()

            if file_record:
                file_path = file_record[0]

                # Delete the file from the local storage
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Delete the file record from the database
                cursor.execute("DELETE FROM file_manager.user_files WHERE id=%s", (file_id,))
                mysql.connection.commit()
                flash("File deleted successfully.", "success")
            else:
                flash("File not found.", "danger")
        except Exception as e:
            flash("Error deleting file: " + str(e), "danger")
        finally:
            cursor.close()

    return redirect(url_for('dashboard'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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

