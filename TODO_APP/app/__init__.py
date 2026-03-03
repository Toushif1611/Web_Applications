#app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#create database object globaly
db = SQLAlchemy()

#create the app factory function
def create_app():
    #create the Flask app
    app = Flask(__name__)

    #configure the app
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #initialize the database with the app
    db.init_app(app)

    #import the routes
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    #create the database tables
    return app
