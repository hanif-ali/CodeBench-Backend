from flask import Blueprint, request
from flask_marshmallow import Marshmallow 
from marshmallow import fields, Schema, pre_dump
from models import Administrator, Assignment, Submission, Student
from flask_jwt_extended import get_jwt_identity
from utils import get_user

serializers_bp = Blueprint("serializers_bp", __name__)

ma = Marshmallow(serializers_bp)




class GroupSchema(ma.Schema):
    class Meta:
        #Fields toexpose
        fields=("id","name")
group_schema=GroupSchema()
groups_schema=GroupSchema(many=True)  

class AdminSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("first_name", "last_name", "email") # Left password
admin_schema = AdminSchema()
admins_schema = AdminSchema(many=True)


class AssignmentSchema(ma.Schema):
    __model__ = Assignment

    id = fields.Int()
    title = fields.Str()
    deadline = fields.DateTime()
    creation_time = fields.DateTime()
    total_submissions = fields.Int()
    submission = fields.Bool()
    total_test_cases = fields.Int()

    @pre_dump
    def add_total_count_or_submission(self, in_data, **kwargs):
        user_type = get_jwt_identity()["mode"]

        # In Admin mode, add total submission count
        if user_type == "admin":
            submissions_count = len(in_data.submissions)
            
            setattr(in_data, "total_submissions", submissions_count)

        # In student mode, add submission status
        else:
            user = get_user(get_jwt_identity())
            common_submissions = Submission.query.filter(
                (Submission.student == user) & (Submission.assignment==in_data)
            ).all()
            setattr(in_data, "submission", len(common_submissions)> 0)

        return in_data

    @pre_dump
    def add_number_of_test_cases(self, in_data, **kwargs):
        test_cases = in_data.test_cases
        setattr(in_data, "total_test_cases", len(test_cases))
        return in_data

assignment_schema=AssignmentSchema()
assignments_schema=AssignmentSchema(many=True)


class StudentSchema(ma.Schema):
    __model__ = Student
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    cms_id = fields.Int()
    email = fields.Str()
    group = fields.Nested(GroupSchema())


student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class SubmissionSchema(ma.Schema):
    __model__ = Assignment

    id = fields.Int()
    student =fields.Nested(StudentSchema())
    submission_time = fields.DateTime()
    test_cases_passed = fields.Int()
    total_test_cases = fields.Int()
    graded = fields.Bool()
    grade_percentage = fields.Int()
    remarks = fields.Str()


submission_schema=SubmissionSchema(exclude=('student.email','student.group', 'student.first_name', 'student.last_name'))
submissions_schema=SubmissionSchema(exclude=('student.email','student.group'),many=True) 

class TestCaseSchema(ma.Schema):
    class Meta:
        fields=("expected_output","expected_input")
        
        
        
test_caseSchema=TestCaseSchema()
test_casesSchema=TestCaseSchema(many=True)        
