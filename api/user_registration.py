from firebase_admin import db
from datetime import datetime, date
import pytz


class UserRegistration:
    def __init__(self, requestJSON):
        self.expectedFields = [
            "first_name",
            "last_name",
            "umass_email",
            "graduation_year",
            "major",
            "github_link",
            "linkedin_link",
            "interest_response",
            "referral_response",
        ]
        self.requestJSON = requestJSON

    def register(self):
        try:
            ref = db.reference("/members/")
            _id = self.requestJSON["umass_email"].replace("@umass.edu", "").lower()
            for field in self.expectedFields:
                ref.child(_id).child(field).set(self.requestJSON[field])
            ref.child(_id).child("joined_on").set(self.getTime())
            return {
                "status": "success",
                "code": 200,
                "message": "Member registered successfully",
                "data": {
                    "first_name": self.requestJSON["first_name"],
                    "last_name": self.requestJSON["last_name"],
                    "umass_email": self.requestJSON["umass_email"],
                },
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process user registration",
            }

    def validate(self):
        ref = db.reference("/members/")
        try:
            passedFields = dict(self.requestJSON).keys()
            missingFields = []
            for field in self.expectedFields:
                if field not in passedFields:
                    missingFields.append(field)
            self.requestJSON["umass_email"] = self.requestJSON["umass_email"].lower()
            if len(missingFields) > 0:
                return {
                    "status": "error",
                    "code": 406,
                    "message": "Required fields are missing: " + str(missingFields),
                }
            if int(self.requestJSON["graduation_year"]) < date.today().year:
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
            _id = self.requestJSON["umass_email"].replace("@umass.edu", "").lower()
            if ref.child(_id).get() != None:
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

    def getTime(self):
        now = datetime.now(pytz.timezone("US/Eastern"))
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return str(dt_string)
