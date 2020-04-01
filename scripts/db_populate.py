"""Populate all the tables with mock data for Testing"""

import sys, os
# Add the application folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import datetime
from flask import Flask, jsonify
from models import db, Student, Administrator, Submission, Assignment, Group

app = Flask(__name__)
app.config['SECRET_KEY']='thisissecretkey'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)


with app.app_context():
    # Administrator Records
    a1 = Administrator(first_name="Hanif", last_name="Ali", email="hanif@abc.com", password="random")
    a2 = Administrator(first_name="Hanif", last_name="Ali", email="saboor@abc.com", password="random")
    db.session.add(a1)
    db.session.add(a2)


    # Group Records
    g1 = Group(name="BESE10B", administrator=a1)
    g2 = Group(name="CESE10C", administrator=a2)
    db.session.add(g1)
    db.session.add(g2)

    # Student Records
    s1 = Student(first_name="Jared", last_name="Dunn", cms_id=234, 
                    email="jared@abc.com", password="random", group=g1)
    s2 = Student(first_name="Shadab", last_name="Khan", cms_id=3332, 
                    email="shaddy@abc.com", password="random", group=g1)
    s3 = Student(first_name="Javed", last_name="Khan", cms_id=432, 
                    email="java@abc.com", password="random", group=g2)
    s4 = Student(first_name="Test", last_name="Name", cms_id=551, 
                    email="testing@abc.com", password="random", group=g2)
    db.session.add(s1)
    db.session.add(s2)
    db.session.add(s3)
    db.session.add(s4)

    # Assignment Records
    deadline = datetime.datetime.now() + datetime.timedelta(days=7) # One week later's date
    as1 = Assignment(title="Assignment1", group=g1, deadline=deadline)
    as2 = Assignment(title="Assignment2", group=g2, deadline=deadline)
    db.session.add(as1)
    db.session.add(as2)

    # Submission Records
    su1 = Submission(student=s1, assignment=as1)
    su2 = Submission(student=s2, assignment=as2)
    db.session.add(su1)
    db.session.add(su2)


    db.session.commit()