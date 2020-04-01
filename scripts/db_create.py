"""Script to create the Database Tables"""

import sys, os
# Include the application folder in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, jsonify
from models import db

app = Flask(__name__)

app.config['SECRET_KEY']='thisissecretkey'

# Database Configurations
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)

with app.app_context():
    db.create_all()