from flask import Flask
from routes import api
from db import init_db
from functions import register_helpers

import os

app = Flask(__name__)
register_helpers(app)

mysql = init_db(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.register_blueprint(api, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
