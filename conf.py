from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging as log

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///supermarket.sqlite3'


db = SQLAlchemy(app)

log.basicConfig(level=log.INFO,
                format='%(asctime)s %(levelname)s %(message)s')


