from firebase_admin import db
from datetime import datetime, date
import pytz


class UserRegistration:
    def __init__(self, requestJSON):
        self.expectedFields = ["first_name", "last_name", "umass_email", "github_link", "linked_link", "major", "grad_year", "ans", "ans2", "extra_field1", "extra_field2"]
        self.requestJSON = requestJSON

    def register(self):
        try:
            ref = db.reference("/")
            email = self.requestJSON["umass_email"].replace("@umass.edu", "")
            for field in self.expectedFields:
                ref.child("Members").child(email).child(field).set(self.requestJSON[field])
            ref.child("Members").child(email).child("joined_on").set(self.getTime())
            return {
                "status": "success",
                "code": 200,
                "message": "Member registered successfully",
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process user registration",
            }

    def validate(self):
        ref = db.reference("/")
        try:
            passedFields = dict(self.requestJSON).keys()
            missingFields = []
            for field in self.expectedFields:
                if field not in passedFields:
                    missingFields.append(field)
            if len(missingFields) > 0:
                return {
                    "status": "error",
                    "code": 406,
                    "message": "Required fields are missing: " + str(missingFields),
                }
            if int(self.requestJSON["grad_year"]) < date.today().year:
                return {
                    "status": "error",
                    "code": 406,
                    "message": "Graduation year has passed",
                }
            if "@umass.edu" not in self.requestJSON["umass_email"]:
                return {
                    "status": "error",
                    "code": 406,
                    "message": "Email is invalid",
                }
            email = self.requestJSON["umass_email"].replace("@umass.edu", "")
            if ref.child("Members").child(email).get() != None:
                return {
                    "status": "error",
                    "code": 409,
                    "message": "Member already registered",
                }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process validation",
            }
        self.validationStatus = True
        return {
            "status": "success",
            "code": 200,
            "message": "Validated details successfully",
        }

    def getTime():
        now = datetime.now(pytz.timezone("US/Eastern"))
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return str(dt_string)
