from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from main import app, db
import sample_config

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def create_sample_config():
    sample_config.create(db)


if __name__ == '__main__':
    manager.run()
