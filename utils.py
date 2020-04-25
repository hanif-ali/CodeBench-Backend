"""Miscellaneous Helper Functions"""
from functools import wraps # To create decorators
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import Student, Administrator, Group, Assignment, Submission

def get_user(jwt_data):
    """Returns the appropriate Student/Administrator record according to mode""" 

    mode = jwt_data["mode"]
    id = jwt_data["id"]
    
    if mode=="admin":
        user = Administrator.query.get(id)
    elif mode=="student":
        user = Student.query.get(id)
    else:
        return None
    return user




def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = get_jwt_identity()
        if data is None:
            return jsonify(status="denied", description="Not Logged In")

        if data['mode'] != 'admin':
            return jsonify(status="error", description="Not in Admin Mode")
        else:
            return fn(*args, **kwargs)
    return wrapper

def student_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        data = get_jwt_identity()
        if data is None:
            return jsonify(status="denied", description="Not Logged In")

        if data['mode'] != 'student':
            return jsonify(status="error", description="Not in Student Mode")
        else:
            return fn(*args, **kwargs)
    return wrapper