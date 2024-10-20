from flask import Flask
from routes import api
from db import init_db


app = Flask(__name__)

mysql = init_db(app)

app.register_blueprint(api, url_prefix='/api')


if __name__ == '__main__':
    app.run(debug=True)
