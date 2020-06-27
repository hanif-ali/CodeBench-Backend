"""Main code containing the starting point of the application along
with all the essential views"""

import os
import time 
from datetime import datetime

from flask import Flask, jsonify, request,json, send_file
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
from serializers import test_caseSchema,test_casesSchema

# Helper Function
from utils import get_user, admin_required, student_required
from utils import run_test
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

# Submissions Directory
app.config['PROJECT_PATH']=os.path.abspath(os.path.dirname(__name__))
app.config['SUBMISSIONS_FOLDER']=os.path.join(app.config["PROJECT_PATH"], "submissions")
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
    return jsonify(student_schema.dump(student))


@app.route("/student/assignments",methods=['GET'])
@jwt_required
@student_required
def get_student_assignments():
    """Returns the assignmets of the currently logged in student"""

    jwt_data = get_jwt_identity()
    student_data = get_user(jwt_data)
    result = student_data.group.assignments
    return jsonify(assignments_schema.dump(result))
    

@app.route("/student/submissions",methods=['GET'])
@jwt_required
@student_required
def get_student_submissions():
    """Returns the submissions of the currently logged in student"""

    student_data = get_user(get_jwt_identity())
    student_submissions = student_data.submissions
    return jsonify(submissions_schema.dump(student_submissions))


@app.route("/student/submissions/<submission_id>",methods=['GET'])
@jwt_required
@student_required
def get_student_submission(submission_id):
    """Returns a single submission of the currently logged in student"""

    student_data = get_user(get_jwt_identity())

    student_submission = Submission.query.filter_by(id=submission_id).first()

    if student_submission is None:
        return jsonify(status="failed", description="Submission does not exist")
    if student_submission.student != student_data:
        return jsonify(status="failed", description="Access Denied")

    return jsonify(submission_schema.dump(student_submission))


@app.route("/student/assignments/<assignment_id>/submit",methods=['POST'])
@jwt_required
@student_required
def make_submission(assignment_id):
    student_data = get_user(get_jwt_identity())
    assignment_data = Assignment.query.filter_by(id=assignment_id).first()

    if not assignment_data:
        return jsonify(status="error", message="Assignment Does not Exist")

    elif assignment_data.group != student_data.group:
        return jsonify(status="error", message="Access Denied")
    submission_object = Submission.query.filter_by(student=student_data).filter_by(assignment=assignment_data).first()
    if not submission_object: 
        # Create Submission
        new_submission_object = Submission(student_data, assignment_data)
        db.session.add(new_submission_object)
        db.session.commit()
    else:
        submission_object.update_for_new_submission()
        new_submission_object=submission_object
        db.session.commit()

    #new_submission_object = Submission(student_data, assignment_data)  # Create Submission
    # We save the object so that we get an id to generate the filename
    #db.session.commit() 

    source_code_object = request.files["source_code"] # From submitted form

    # Make use of a utility function we defined in models.py
    file_path = new_submission_object.get_submission_filename()

    # Save the file
    source_code_object.save(file_path)

    try:
        execution_results = run_test(new_submission_object, assignment_data)
    except:
        # Revert Database Change
        source_code_object.delete()
        raise       # Reraise error

    return jsonify(execution_results)


@app.route('/student/submissions/<submission_id>/results',methods=['GET'])
@jwt_required
@student_required
def student_submission_results(submission_id):
    
    jwt_data = get_jwt_identity()
    student_data = get_user(jwt_data)

    submission_data=Submission.query.filter_by(id=submission_id).first()

    if submission_data is None:
        return jsonify(status="Failed",message="Submission Does Not Exist")

    if submission_data.student != student_data or not submission_data.graded:
        return jsonify(status="Failed", message="Access Denied")

    submission_results_path = submission_data.get_submission_result_path()

    return send_file(submission_results_path)

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
    return jsonify(admin_schema.dump(admin))


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

@app.route("/admin/assignments/<assignment_id>/submissions",methods=['GET'])
@jwt_required
@admin_required 
def admin_assigments(assignment_id):
    """Returns submissions for the Assignment specified by id"""

    admin_assigment=Assignment.query.filter_by(id=assignment_id).first()
    data=admin_assigment.submissions

    return jsonify(submissions_schema.dump(data))


@app.route("/admin/assignments/new",methods=['POST'])
@jwt_required
@admin_required 
def create_assignment():
    # Get Administrator Data. Needed to verify Group Permission
    admin_data = get_user(get_jwt_identity())

    # Get Assignment Data
    assignment_data = request.get_json()

    # Convert the Given ISO DataTime to Python DateTime object
    try:
        py_deadline = datetime(*time.strptime(assignment_data['deadline'] , "%Y-%m-%dT%H:%M")[:6])
    except ValueError:
        return jsonify(status="Error", description="Invalid DateTime")

    # Find out the Assignment Group selected
    assignment_group = Group.query.get(assignment_data['group_id'])

    # If do not have right permissions
    if (assignment_group is None or assignment_group.administrator != admin_data):
        return jsonify(status="error", message="Access Denied")

    linting_percentage = assignment_data.get("linting") or 0
    time_limit = assignment_data.get("time_limit") or 0

    if (linting_percentage > 100) or (linting_percentage < 0):
        return jsonify(status="Error", description="Invalid Linting Percentage")

    # Create New Assignment
    new_assignment = Assignment(title=assignment_data['title'], 
                                group=assignment_group,
                                deadline = py_deadline,
                                linting = linting_percentage,
                                time_limit = time_limit)

    # List used to store test_cases temporarily
    # so they are not destructed beforing database commit
    test_cases = []
    for test_case in assignment_data['test_cases']:
        new_test_case = TestCase(assignment=new_assignment, # Link to the Assignment
                                exp_input=test_case["input"],
                                exp_output=test_case["output"],
                                 visible=test_case["visible"])
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
    if assignment_data.group.admin != admin:
        return {
            "status": "error",
            "message": "Access Denied"
        }

    db.session.delete(assignment_data)
    db.session.commit()
    return jsonify({"status": "succes",
                    "message":"Deleted"})    

@app.route("/admin/assignment/edit/<assignment_id>",methods=['POST'])
@jwt_required
@admin_required
def edit_assignment(assignment_id):
    
    req=request.get_json()
    
    data_assingments=Assignment.query.filter_by(id=assignment_id).first()
    
    
    if not data_assingments:
        return jsonify(status="error",message="Assigment does not exists")
    #edited the title
    data_assingments.title=req['title']
    #edited the time
    data_assingments.deadline=datetime(*time.strptime(req['deadline'] ,"%Y-%m-%d %H:%M")[:6])
    #query for test cases
    test_cases=TestCase.query.filter_by(assignment_id=assignment_id)
            
    x=0      
    for each in test_cases:
            #edited each test case
            each.expected_input= req["test_cases"][x].get("expected_input")
            each.expected_output=req["test_cases"][x].get("expected_output" )
            x=x+1
    db.session.commit()
    return jsonify(status="Success",message="Edited")


@app.route('/admin/submissions/<submission_id>',methods=['GET'])
@jwt_required
@admin_required
def submission_details(submission_id):
    
    submission_data=Submission.query.filter_by(id=submission_id).first()

    if submission_data is None:
        return jsonify(status="Failed",message="Submission Does Not Exist")

    return jsonify(submission_schema.dump(submission_data))         


@app.route('/admin/submissions/<submission_id>/grade',methods=['POST'])
@jwt_required
@admin_required
def grade_submission(submission_id):

    admin_data = get_user(get_jwt_identity())

    post_data = request.get_json()
    try:
        submission_grade = int(post_data.get("submission_grade"))
        remarks = post_data.get("remarks")

    except:
        return jsonify(status="Failed", description="Invalid Grade")

    if submission_grade is None or (0 > submission_grade or submission_grade > 100):
        return jsonify(status="Failed", description="Invalid Grade")

    submission_data=Submission.query.filter_by(id=submission_id).first()

    if submission_data is None:
        return jsonify(status="Failed", description="Submission Does Not Exist")

    if submission_data.assignment.group.administrator != admin_data:
        return jsonify(status="Failed", description="Access Denied")

    submission_data.graded = True
    submission_data.grade_percentage = submission_grade
    submission_data.remarks = remarks
    db.session.commit()

    return jsonify(status="Success", description="Graded")

@app.route('/admin/submissions/<submission_id>/file',methods=['GET'])
@jwt_required
@admin_required
def submission_file(submission_id):
    
    submission_data=Submission.query.filter_by(id=submission_id).first()
    if submission_data is None:
        return jsonify(status="Failed",message="Submission Does Not Exist")

    submission_file_path = submission_data.get_submission_filename()

    return send_file(submission_file_path)


@app.route('/admin/submissions/<submission_id>/results',methods=['GET'])
@jwt_required
@admin_required
def submission_results(submission_id):
    
    submission_data=Submission.query.filter_by(id=submission_id).first()
    if submission_data is None:
        return jsonify(status="Failed",message="Submission Does Not Exist")

    submission_results_path = submission_data.get_submission_result_path()

    return send_file(submission_results_path)

@app.route('/admin/assignment/test_cases/<ass_id>',methods=['GET'])
@jwt_required
@admin_required
def test_Cases(ass_id):
    
    ass=Assignment.query.filter_by(id=ass_id).first()
    return jsonify(test_casesSchema.dump(ass.test_cases))

if __name__=="__main__":
    app.run()
