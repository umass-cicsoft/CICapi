from firebase_admin import db
from datetime import datetime, date
import pytz
import uuid


class UserTechPoll:
    def __init__(self, requestJSON):
        self.expectedFields = [
            "poll_value"
        ]
        self.requestJSON = requestJSON

    def poll(self):
        try:
            ref = db.reference("/technology_poll/")
            _id = str(uuid.uuid4()).replace("-", "")
            for field in self.expectedFields:
                ref.child(_id).child(field).set(self.requestJSON[field])
            ref.child(_id).child("submitted_on").set(self.getTime())
            return {
                "status": "success",
                "code": 200,
                "message": "Technology poll submitted successfully",
                "data": {
                    "poll_value": self.requestJSON["poll_value"],
                    "submitted_on": str(ref.child(_id).child("submitted_on").get()),
                },
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process technology poll.",
            }

    def getTime(self):
        now = datetime.now(pytz.timezone("US/Eastern"))
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return str(dt_string)
