# Tutoring API

## Installation and Setup

### Setup code base

Install [Python 2.7](https://www.python.org/download/releases/2.7/) and [pip](https://pypi.python.org/pypi/pip)

Set up [Virtualenv](https://virtualenv.pypa.io/en/stable/):

    $ pip install virtualenv
    $ virtualenv env
    $ source env/bin/activate

Install project dependencies:

    $ pip install -r requirements.txt

### Setup dependencies

#### Mysql

Install [mysql 5.7](https://dev.mysql.com/downloads/mysql/5.7.html) and run the server:

    $ mysql.server start

Create a local development database:

    $ mysql -u root
    mysql> create database thesis

#### Redis
Download and install Redis follow this [link](https://redis.io/download) or these bellow commands (recommended)

    $ wget http://download.redis.io/releases/redis-4.0.7.tar.gz
    $ tar xzf redis-4.0.7.tar.gz
    $ cd redis-4.0.7
    $ sudo make install

Start redis server using this command

    redis-server

#### Celery
Start celery tasks

    $ celery -A main.celery worker --pool=solo --loglevel=INFO

### Migrate database
Run database migrations:

    $ python manage.py db upgrade

To create database migrations after changing models:

    $ python manage.py db migrate

### Create sample configs
To create all sample configs

    $ python manage.py create_sample_config
 
## Local development

To start an instance of the server running on your local machine:

    $ python run.py

The APIs are now available at [localhost:8000](http://localhost:8000)
