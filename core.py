"""Main code containing the starting point of the application along
with all the essential views"""

from flask import Flask, jsonify, request
from models import db, Student, Administrator, Group, Assignment, Submission

# JWT Imports
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from serializers import serializers_bp, student_schema, students_schema, admin_schema, admins_schema,assisngment_schema,assignments_schema,group_schema,groups_schema,submissions_schema,submission_schema,SubmissionSchema
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


@app.route("/student/details")
@jwt_required
@student_required
def student_details():
    """Returns the details of the currently logged in  Student"""

    jwt_data = get_jwt_identity()
    student = get_user(jwt_data)
    return student_schema.dumps(student)


@app.route("/admin/details")
@jwt_required
@admin_required
def admin_details():
    """Returns the details of the currently logged in  Admin"""

    jwt_data = get_jwt_identity()
    admin = get_user(jwt_data)
    return admin_schema.dumps(admin)

@app.route("/students/assignments",methods=['GET'])
@jwt_required
@student_required
def Student_assingmnet_details():
    """Returns the assignmets of the currently logged in  students"""

    jwt_data = get_jwt_identity()
    data = get_user(jwt_data)
    result=data.group.assignments
    return jsonify(assignments_schema.dumps( data.group.assignments))
    
@app.route("/admin/assignments/<assingments_id>/submission",methods=['GET'])
@jwt_required
@admin_required 
def admin_assigments(assingments_id):

    """Returns the assignments of the provided id"""

    admin_assigment=Assignment.query.filter_by(id=assingments_id).first()
    data=admin_assigment.submissions
    
    return jsonify({"submission":submissions_schema.dumps(data)})
    


@app.route("/admin/groups",methods=['GET'])
@jwt_required
@admin_required   
def getGRoups():

    """Returns the details of the groups ofcurrently logged in  Admin"""
    
    data=Group.query.all()
    return jsonify({"status":"succes" ,"groups":groups_schema.dumps(data,indent=2)})

@app.route("/admin/groups/<group_id>/assignments", methods=['GET'])
@jwt_required
@admin_required  
def getAssignments(group_id):
    
    """Returns the details of the specific group logged in  Admin"""

    data=Group.query.filter_by(id=group_id).first()
    data_assignment=data.assignments
    if data==None:
        return jsonify({"key":"failed"})
    return jsonify({"status":"succes","group_name":data.name,"assignments":assignments_schema.dumps(data_assignment)})


@app.route("/admin/assignment/edit/<assinment_id>",methods=['POST'])
@jwt_required
@admin_required  
def editAssignment(assinment_id):

    """Edit assingmnet Title and Deadline logged in as Admin"""

    req=request.get_json()
    data_assingments=Assignment.query.filter_by(id=assinment_id).first()
    if data_assingments is None:
        return {"messgae":"NO assignments exists"}
    data_assingments.title=req['title']
    data_assingments.deadline=req['deadline']
    return jsonify({"message":"Edited"})

@app.route("/admin/assignment/delete/<assinment_id>",methods=['POST'])
@jwt_required
@admin_required  
def deleteAssignment(assinment_id):

    """Delete assingmnet  logged in as Admin"""

    data_assingments=Assignment.query.filter_by(id=assinment_id).first()
    if data_assingments is None:
        return {"messgae":"NO assignments exists"}
    db.session.delete(data_assingments)
    db.session.commit()
    return jsonify({"message":"Deleted"})    



     




if __name__=="__main__":
    app.run()