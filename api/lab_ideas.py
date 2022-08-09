from firebase_admin import db
from datetime import datetime, date
import pytz
import uuid


class LabIdeas:
    def __init__(self, requestJSON, request):
        self.expectedFields = [
            "first_name",
            "last_name",
            "idea_text",
            "ip_address"
        ]
        self.ipAddress = request.access_route if len(request.headers.getlist("X-Forwarded-For")) == 0 else request.headers.getlist("X-Forwarded-For")[0]
        self.requestJSON = requestJSON
        self.requestJSON["ip_address"] = self.ipAddress

    def idea(self):
        try:
            ref = db.reference("/lab_ideas/")
            _id = str(uuid.uuid4()).replace("-", "")
            for field in self.expectedFields:
                ref.child(_id).child(field).set(self.requestJSON[field])
            ref.child(_id).child("submitted_on").set(self.getTime())
            return {
                "status": "success",
                "code": 200,
                "message": "Lab idea submitted successfully",
                "data": {
                    "idea_text": self.requestJSON["idea_text"],
                    "submitted_on": str(ref.child(_id).child("submitted_on").get())
                },
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process lab idea suggestion",
            }

    def getTime(self):
        now = datetime.now(pytz.timezone("US/Eastern"))
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return str(dt_string)
