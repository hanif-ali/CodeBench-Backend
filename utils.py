"""Miscellaneous Helper Functions"""
from functools import wraps # To create decorators
import subprocess
import io
import json

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

#helper function that returns dictionary containing details of the submission 
def run_test(submission_object):
    #######################
    # NOT COMPLETED YET
    #######################

    # Halfway through
    submission_id = submission_object.id
    submission_file = submission_object.get_submission_filename()
    test_cases = submission_object.assignment.test_cases

#dictionary to store data of passed cases 
    test_cases = {}
    result = {"test_cases": test_cases,
              "student_id": submission_object.student.id,
              "test_cases": []
            }
   
    for test_case in test_cases:

        #subprocess to compile the given submitted file and run the test cases on it
        test_process = subprocess.Popen(['python', submission_file], stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        #provided test cases from the admin
        expected_input = test_case.expected_input
        expected_output = test_case.expected_output   

        #checking of the test cases
        output=test_process.communicate(input=expected_input.encode())[0]
        

        #information to be returned 
        passed = output.decode() == expected_output
        output = output.decode().strip()

        exit_code = test_process.wait()

        result.test_cases.append({
            "passed": passed,
            "expected_input": expected_input,
            "expected_output": expected_output,
            "output": output
        })

    json_file_path = submission_object.get_submission_result_path() # get the pathname from the model

    with open(json_file_path, "w+") as json_file:
        json_file.write(json.dumps(result)) # Serialize object and write to .json file


    return result    