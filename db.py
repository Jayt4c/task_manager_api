import os
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

mysql = MySQL()
secret_key = os.urandom(24)

def init_db(app):
    mysql = MySQL(app)
    #configurations
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_DATABASE'] = os.getenv('MYSQL_DATABASE')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.secret_key = os.getenv('SECRET_KEY')
    
    return mysql