import pusher
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import config

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)

CORS(app)

pusher_client = pusher.Pusher(
    app_id=config.PUSHER_APP_ID,
    key=config.PUSHER_KEY,
    secret=config.PUSHER_SECRET
)

from main.models import *
import main.controllers
import main.errors
