from firebase_admin import db
from datetime import datetime, date
import pytz
import uuid


class labIdeas:
    def __init__(self, requestJSON, request):
        self.expectedFields = [
            "first_name",
            "last_name",
            "idea_text"
        ]
        self.requestJSON = requestJSON

    def idea(self):
        try:
            ref = db.reference("/lab_ideas/")
            _id = str(uuid.uuid4()).replace("-", "")
            for field in self.expectedFields:
                ref.child(_id).child(field).set(self.requestJSON[field])
            return {
                "status": "success",
                "code": 200,
                "message": "Idea submitted successfully",
                "data": {
                    "first_name": self.requestJSON["first_name"],
                    "last_name": self.requestJSON["last_name"],
                    "idea_text": self.requestJSON["idea_text"]
                },
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process idea.",
            }
