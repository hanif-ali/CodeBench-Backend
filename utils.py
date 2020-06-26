"""Miscellaneous Helper Functions"""
from functools import wraps # To create decorators
import subprocess
import io
import json
from math import exp
from time import time

from pylint.lint import Run as LinterRun

from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import Student, Administrator, Group, Assignment, Submission

def normalize_linter_score(number):
    return 1/(1+exp(-number))


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
def run_test(submission_object, assignment_object):

    submission_id = submission_object.id
    submission_file = submission_object.get_submission_filename()

    time_limit = assignment_object.time_limit

    test_cases = []
    result = {
              "test_cases": test_cases,
              "student_id": submission_object.student.id,
              "test_cases_passed": 0
            }

    for test_case in assignment_object.test_cases:

        start = time()
        ##in case file is for python compiler
        if (submission_file.split("."))[-1] == "py":
            #subprocess to compile the given submitted file and run the test cases on it
            test_process = subprocess.Popen(['python', submission_file], stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            #in case file is for java compiler
            test_process =subprocess.Popen(["C:\\Program Files\\Java\\jdk-14.0.1\\bin\\java.exe",submission_file], shell=True,stdout=subprocess.PIPE
            ,stdin=subprocess.PIPE, stderr=subprocess.PIPE)


        # Provided test cases from the admin
        expected_input = test_case.expected_input
        expected_output = test_case.expected_output
        visible = test_case.visible

        #checking of the test cases
        output=test_process.communicate(input=expected_input.encode())[0]

        #information to be returned 
        output = output.decode().strip()
        passed = output == expected_output

        exit_code = test_process.wait()
        end = time()

        time_elapsed = end-start
        if (time_limit > 0) and (time_elapsed > time_limit):
            output = "TIME LIMIT EXCEEDED"
            passed = False

        test_cases.append({
            "passed": passed,
            "expected_input": expected_input,
            "expected_output": expected_output,
            "output": output,
            "visible": visible,
            "time_elapsed": time_elapsed
        })

    # Count the number of Test Cases that Passed
    result["test_cases_passed"] = list(map(lambda a:a["passed"], test_cases)).count(True)
    # Count number of total test cases
    result["total_test_cases"] = len(test_cases)


    linter_percentage = assignment_object.linting
    tc_percentage = 100 - linter_percentage

    try:
        tc_score = result["test_cases_passed"] * 100 / result["total_test_cases"]
    except ZeroDivisionError: tc_score = 100
    linter_score = 0

    if assignment_object.linting > 0:
        linter_results = LinterRun([submission_file], do_exit=False)
        linter_score = normalize_linter_score(linter_results.linter.stats['global_note'])

    tc_score_scaled = (tc_score/100) * tc_percentage
    linter_score_scaled = linter_score * linter_percentage

    total_score = linter_score_scaled + tc_score_scaled

    result["percentages"] = {
        "test_cases": tc_percentage,
        "linter": linter_percentage
    }

    result["scores"] = {
        "overall": total_score,
        "linter": linter_score_scaled,
        "test_cases": tc_score_scaled
    }
    result["time_limit"] = time_limit

    # Write Results to a JSON File
    json_file_path = submission_object.get_submission_result_path() # get the pathname from the model
    with open(json_file_path, "w+") as json_file:
        json_file.write(json.dumps(result)) # Serialize object and write to .json file

    visible_test_cases = list(filter(lambda x: x["visible"], test_cases))

    return {
        "status": "success",
        "percentages": result["percentages"],
        "scores": result["scores"],
        "total_test_cases": result["total_test_cases"],
        "test_cases_passed": result["test_cases_passed"],
        "visible_test_cases": visible_test_cases,
        "time_limit": time_limit
    }
