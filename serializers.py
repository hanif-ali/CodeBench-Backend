from flask import Blueprint
from flask_marshmallow import Marshmallow

serializers_bp = Blueprint("serializers_bp", __name__)

ma = Marshmallow(serializers_bp)

class StudentSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("first_name", "last_name", "cms_id", "email") # Left group, password


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)


class AdminSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("first_name", "last_name", "email") # Left password

admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)
