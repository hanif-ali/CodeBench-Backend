"""Miscellaneous Helper Functions"""
from functools import wraps # To create decorators
import subprocess
import io

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


def run_test(submission_object):
    #######################
    # NOT COMPLETED YET
    #######################

    # Halfway through
    submission_id = submission_object.id
    submission_file = submission_object.get_submission_filename()
    test_cases = submission_object.assignment.test_cases

    for test_case in test_cases:
        expected_input = test_case.expected_input
        expected_output = test_case.expected_output

    test_process = subprocess.Popen(['python', submission_file], stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    test_process.communicate(input="Hahnif\n")[0]
    test_process.communicate(input="4\n")[0]
    exit_code = test_process.wait()
    print(f"Finished with exit code of {exit_code}")
    print(test_process.stdout.read())


    return [1, 2]
