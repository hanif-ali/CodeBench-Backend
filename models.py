from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
import datetime

db=SQLAlchemy()

class Student(db.Model):
    """Account Models for Students"""

    id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(50))
    cms = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    group = db.relationship("Group", backref="students")

    def __init__(self,name,cms,email,password,course,id):
        self.id=id
        self.name=name
        self.course=course
        self.cms=cms
        self.email=email
        self.password=password

class Administrator(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    email = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    group = db.Column(db.String(50)) 

    def __init__(self,name,email,password,course,id):
        self.id=id
        self.name=name
        self.course=course
        self.email=email
        self.password=password


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(50))
    administrator = db.relationship("Administrator", backref="groups")

    def __init__(self, name, administrator):
        self.name = name 
        self.administator = adminisrtator


class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    title = db.Column(db.String(50))
    group = db.relationship("Group", backref="assignments")
    # datetime.datetime.now acts as a callback function called everytime the 
    # object is created
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    deadline = db.Column(db.DateTime)

    def __init__(self, title, group, deadline):
        self.title = title
        self.group = group
        self.deadline = deadline


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    student = db.relationship("Student", backref="submissions")
    submission_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, student, submission_time):
        self.student = student
        self.submission_time = submission_time