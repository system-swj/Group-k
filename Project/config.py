import os

basedir = os.path.abspath(os.path.dirname(__file__))

# MySQL configuration for XAMPP
SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/voting_app'
SQLALCHEMY_TRACK_MODIFICATIONS = False