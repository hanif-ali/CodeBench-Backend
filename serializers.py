from flask import Blueprint
from flask_marshmallow import Marshmallow 
from marshmallow import fields, Schema, pre_dump
from models import Administrator, Assignment

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
    __model__ = Assignment

    id = fields.Int()
    title = fields.Str()
    deadline = fields.DateTime()
    creation_time = fields.DateTime()
    total_submissions = fields.Int();

    @pre_dump
    def add_total_count(self, in_data, **kwargs):
        submissions_count = len(in_data.submissions)
        setattr(in_data, "total_submissions", submissions_count)
        return in_data

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

    


