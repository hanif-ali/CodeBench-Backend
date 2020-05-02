"""Contains all the Models for the Project

Student - Authentication Model for Users who can do submissions
Administrator - Authentication Model for Users who can create assignments 
Group - Model for a Class/Course
Assignment - Model for storing basic details of the Assignment
Submission - Individual solutions submitted by a Student

A 'Student' can be part of a single 'Group'. Each 'Group' needs to have a single
'Administrator'. A 'Group' can have multiple 'Assignment's added by the 'Administrator'

All Passwords are stored as hashes 
"""

from flask_sqlalchemy import SQLAlchemy
# Password hashing functions used in functions in authentication models 
from werkzeug.security import generate_password_hash,check_password_hash
import datetime

db=SQLAlchemy()

class Student(db.Model):
    __tablename__ = "students"

    # Normal Data Fields
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    cms_id = db.Column(db.Integer, unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

    # Foreign Key Relationships
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    group = db.relationship("Group", backref="students")

    def __init__(self, first_name, last_name, cms_id, email, password, group):
        self.first_name = first_name
        self.last_name = last_name
        self.cms_id = cms_id
        self.email = email
        self.password = generate_password_hash(password)
        self.group = group
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Administrator(db.Model):
    __tablename__ = "administrators"

    id = db.Column(db.Integer,primary_key=True,nullable=False)
    email = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(50))

    # Foreign Key Relationships
    administrator_id = db.Column(db.Integer, db.ForeignKey('administrators.id'))
    administrator = db.relationship("Administrator", backref=db.backref("groups", uselist=True))

    def __init__(self, name, administrator):
        self.name = name 
        self.administrator = administrator


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True, nullable=True)
    title = db.Column(db.String(50))
    # datetime.datetime.now acts as a callback function called everytime the 
    # object is created
    creation_time = db.Column(db.DateTime, default=datetime.datetime.now)
    deadline = db.Column(db.DateTime)

    # Foreign Key Relationships
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    group = db.relationship("Group", backref="assignments")

    def __init__(self, title, group, deadline):
        self.title = title
        self.group = group
        self.deadline = deadline


class Submission(db.Model):
    __tablename__ = "submssions"

    id = db.Column(db.Integer, primary_key=True, nullable=True)
    submission_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Foreign Key Relationships
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    student = db.relationship("Student", backref="submissions")

    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"))
    assignment = db.relationship("Assignment", backref="submissions")


    def __init__(self, student, assignment):
        self.student = student
        self.assignment = assignment


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True, nullable=True)
    expected_input = db.Column(db.String, default="")
    expected_output = db.Column(db.String)

    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"))
    assignment = db.relationship("Assignment", backref="test_cases")

    def __init__(self, assignment, exp_input, exp_output):
        self.expected_input = exp_input
        self.expected_output = exp_output
        self.assignment = assignment