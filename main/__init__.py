from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import config

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)

CORS(app)

from main.models import *
