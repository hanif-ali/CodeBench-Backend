from flask import Blueprint
from flask_marshmallow import Marshmallow
from marshmallow import fields,Schema
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


class AssignmetSchema(ma.Schema):
    class Meta:
            #Fields toexpose
            fields=("title","deadline","creation","id")
assisngment_schema=AssignmetSchema()
assignments_schema=AssignmetSchema(many=True)

class GroupSchema(ma.Schema):
    class Meta:
        #Fields toexpose
        fields=("id","name")
group_schema=GroupSchema()
groups_schema=GroupSchema(many=True)  

class SubmissionSchema(ma.Schema):
    class Meta:
            fields=("id","submission_time","student")
            
    student =fields.Nested(StudentSchema,only=("first_name","last_name"))    
        
        
submission_schema=SubmissionSchema()
submissions_schema=SubmissionSchema(many=True) 

    


