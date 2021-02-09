from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


from config import config

app = Flask(__name__)
app.config.from_object(config)

_naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

_metadata = MetaData(naming_convention=_naming_convention)
db = SQLAlchemy(app=app,
                metadata=_metadata,
                session_options={"expire_on_commit": True})

CORS(app)


# Register these in their own function so they don't pollute
# the main namespace
# Loading these here lets sqlalchemy know about the models
# and allows the controllers/errors to execute their hooks to
# create the routes
def _register_subpackages():
    import main.models
    import main.errors
    import main.controllers


_register_subpackages()
