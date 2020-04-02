"""Contains routes for testing the applications while building it"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Student
from serializers import students_schema
from utils import get_user, admin_required, student_required

bp = Blueprint("test_routes", __name__)

@bp.route("/users")
def students():
    all_users = Student.query.all()
    return jsonify(students_schema.dump(all_users))

@bp.route("/test")
@jwt_required
def test_login_identity():
    """Test View to check login identity"""

    login_details = get_jwt_identity()
    user = get_user(login_details["mode"], login_details["id"])
    response = "You are logged in {} mode as {}".format(login_details["mode"].upper(),
                                                user.first_name)
    return response