"""Main code containing the starting point of the application along
with all the essential views"""

import os
import time 
from datetime import datetime

from flask import Flask, jsonify, request
from models import db, Student, Administrator, Group, Assignment, Submission, TestCase

# JWT Imports
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from serializers import serializers_bp, student_schema, students_schema, \
                        admin_schema, admins_schema,assignment_schema, \
                        assignments_schema,group_schema,groups_schema, \
                        submissions_schema,submission_schema

# Helper Function
from utils import get_user, admin_required, student_required
from test_routes import bp as test_routes_bp


app = Flask(__name__)
# Register Blueprints
app.register_blueprint(serializers_bp)
app.register_blueprint(test_routes_bp)

# App configs
app.config['SECRET_KEY']='thisissecretkey'
app.debug = True  # True only for development

# Database Configs
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app) 

# JWT for Authentication
jwt = JWTManager(app)

# --------------------------------------------
#         Authentication Routes
# --------------------------------------------
@app.route("/login", methods=['POST'])
def login():

    """Login view for both Administrators and Students

    Accepts a JSON request with the following fields:
     - mode: 'admin' or 'student
     - email: The unique email address of a user
     - password   
     """

    data = request.get_json()
    if data is None:
        # This happens when the request's type is not JSON
        return jsonify(status="error", description="Invalid Request")

    email = data.get("email")
    password = data.get("password")
    mode = data.get("mode")

    # Check if any fields is None
    if not(all((email, password, mode))):
        return jsonify(status="error", description="All fields are not provided")

    # Mode can only  be either of the two
    if mode not in ("admin", "student"):
        return jsonify(status="error", description="Mode must be student/admin")

    if mode == "student":
        user = Student.query.filter_by(email=email).first()
    else:
        user = Administrator.query.filter_by(email=email).first()

    if not user:
        return jsonify(status="denied", description="Email Invalid")

    if user.check_password(password):
        access_token = create_access_token(identity={"mode":mode, "id":user.id})
        return jsonify(status="success", access_token=access_token)
    else:
        return jsonify(status="denied", description="Password Invalid")




# --------------------------------------------
#           Student Routes
# --------------------------------------------

@app.route("/student/details")
@jwt_required
@student_required
def student_details():
    """Returns the details of the currently logged in  Student"""

    jwt_data = get_jwt_identity()
    student = get_user(jwt_data)
    return student_schema.dumps(student)


@app.route("/student/assignments",methods=['GET'])
@jwt_required
@student_required
def get_student_assignments():
    """Returns the assignmets of the currently logged in student"""

    jwt_data = get_jwt_identity()
    student_data = get_user(jwt_data)
    result = student_data.group.assignments
    return assignments_schema.dumps(result)
    

@app.route("/student/submissions",methods=['GET'])
@jwt_required
@student_required
def get_student_submissions():
    """Returns the submissions of the currently logged in student"""

    student_data = get_user(get_jwt_identity())
    student_submissions = student_data.submissions
    return submissions_schema.dumps(student_submissions)

# --------------------------------------------
#           Admin Routes
# --------------------------------------------

@app.route("/admin/details")
@jwt_required
@admin_required
def admin_details():
    """Returns the details of the currently logged in  Admin"""

    jwt_data = get_jwt_identity()
    admin = get_user(jwt_data)
    return admin_schema.dumps(admin)


@app.route("/admin/groups",methods=['GET'])
@jwt_required
@admin_required   
def get_groups():

    """Returns the details of the groups ofcurrently logged in  Admin"""
    
    # Retrieve the admin object
    admin = get_user(get_jwt_identity())
    groups_data = admin.groups

    return jsonify(groups_schema.dump(groups_data))


@app.route("/admin/groups/<group_id>/assignments", methods=['GET'])
@jwt_required
@admin_required  
def get_assignments(group_id):
    """Returns the assignments of the group specified by group_id"""

    # Get the Administrator Object
    admin_data = get_user(get_jwt_identity())

    # Get the group data
    group_data = Group.query.filter_by(id=group_id).first()
    if group_data is None:
        return jsonify(status="error", message="No such Group")

    # Check if admin owns that group
    if group_data.administrator != admin_data:
        return jsonify(status="error", message="Access Denied")

    return jsonify(assignments_schema.dump(group_data.assignments))


@app.route("/admin/assignments/<assignment_id>", methods=['GET'])
@jwt_required
@admin_required  
def get_assignment(assignment_id):
    """Returns the assignments of the group specified by group_id"""

    # Get the Administrator Object
    admin_data = get_user(get_jwt_identity())

    # Get the Assignment data
    assignment_data = Assignment.query.filter_by(id=assignment_id).first()
    if assignment_data is None:
        return jsonify(status="error", message="No such Assignment")

    # Check if admin owns that group
    if assignment_data.group.administrator != admin_data:
        return jsonify(status="error", message="Access Denied")

    return jsonify(assignment_schema.dump(assignment_data))

@app.route("/admin/assignments/<assingment_id>/submissions",methods=['GET'])
@jwt_required
@admin_required 
def admin_assigments(assingments_id):
    """Returns submissions for the Assignment specified by id"""

    admin_assigment=Assignment.query.filter_by(id=assingments_id).first()
    data=admin_assigment.submissions

    return jsonify({"submission":submissions_schema.dumps(data)})


@app.route("/admin/assignments/new",methods=['POST'])
@jwt_required
@admin_required 
def create_assignment():
    # Get Administrator Data. Needed to verify Group Permission
    admin_data = get_user(get_jwt_identity())

    # Get Assignment Data
    assignment_data = request.get_json()

    # Convert the Given ISO DataTime to Python DateTime object
    py_deadline = datetime(*time.strptime(assignment_data['deadline'] , "%Y-%m-%dT%H:%M")[:6])

    # Find out the Assignment Group selected
    assignment_group = Group.query.get(assignment_data['group_id'])

    # If do not have right permissions
    if (assignment_group is None or assignment_group.administrator != admin_data):
        return jsonify(status="error", message="Access Denied")

    # Create New Assignment
    new_assignment = Assignment(title=assignment_data['title'], 
                                group=assignment_group,
                                deadline = py_deadline)

    # Array used to store test_cases temporarily
    test_cases = []
    for test_case in assignment_data['test_cases']:
        new_test_case = TestCase(assignment=new_assignment, # Link to the Assignment
                                exp_input=test_case["input"],
                                exp_output=test_case["output"])
        test_cases.append(test_case)

    # Save all the changes
    db.session.commit()
    return jsonify(status="success", message="Assignment Created")


@app.route("/admin/assignment/delete/<assignment_id>",methods=['POST'])
@jwt_required
@admin_required  
def delete_assignment(assignment_id):
    """Delete The Assignment specified by assignment_id"""

    jwt_data = get_jwt_identity();
    admin = get_user(jwt_data)

    assignment_data = Assignment.query.filter_by(id=assignment_id).first()

    # If no such assignment
    if not assignment_data:
        return {"status": "error", 
                "messgae":"Assignment Not Found"}

    # Check if the user is Admin of the Group
    if assignment.group.admin != admin:
        return {
            "status": "error",
            "message": "Access Denied"
        }

    db.session.delete(data_assingments)
    db.session.commit()
    return jsonify({"status": "succes",
                    "message":"Deleted"})    


@app.route("/admin/assignment/edit/<assinment_id>",methods=['POST'])
@jwt_required
@admin_required  
def edit_assignment(assignment_id):

    req=request.get_json()
    data_assingments=Assignment.query.filter_by(id=assinment_id).first()
    if data_assingments is None:
        return {"messgae":"NO assignments exists"}
    data_assingments.title=req['title']
    data_assingments.deadline=req['deadline']
    return jsonify({"message":"Edited"})



if __name__=="__main__":
    app.run()