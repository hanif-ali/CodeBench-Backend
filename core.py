"""Main code containing the starting point of the application along
with all the essential views"""

from flask import Flask, jsonify, request
from models import db, Student, Administrator, Group, Assignment, Submission

# JWT Imports
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

# Helper Function
from utils import get_user


app = Flask(__name__)
app.config['SECRET_KEY']='thisissecretkey'
app.debug = True  # True only for development

# Database Configs
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app) 

# JWT for Authentication
jwt = JWTManager(app)


@app.route("/test")
@jwt_required
def test_login_identity():
    """Test View to check login identity"""

    login_details = get_jwt_identity()
    user = get_user(login_details["mode"], login_details["id"])
    response = "You are logged in {} mode as {}".format(login_details["mode"].upper(),
                                                user.first_name)
    return response


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



if __name__=="__main__":
    app.run()