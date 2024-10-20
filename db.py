from flask_mysqldb import MySQL

mysql = MySQL()

def init_db(app):
    mysql = MySQL(app)
    #configurations
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['USER'] = 'root'
    app.config['PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'mydatabase'
    app.secret_key = 'your_secret_key'
    
    return mysql