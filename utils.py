"""Miscellaneous Helper Functions"""

from models import Student, Administrator, Group, Assignment, Submission

def get_user(mode, id):
    """Returns the appropriate Student/Administrator record according to mode""" 

    if mode=="admin":
        user = Administrator.query.get(id)
    elif mode=="student":
        user = Student.query.get(id)
    else:
        return None
    return user