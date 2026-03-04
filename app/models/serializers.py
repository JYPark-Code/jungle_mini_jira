# models/serializer.py
def serialize_issue(issue):

    issue["_id"] = str(issue["_id"])
    issue["project_id"] = str(issue["project_id"])

    return issue