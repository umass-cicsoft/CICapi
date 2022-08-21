from firebase_admin import db
from datetime import datetime, date
import pytz


class CoreTeamApplication:
    def __init__(self, requestJSON):
        self.expectedFields = [
            "first_name",
            "last_name",
            "umass_email",
            "graduation_year",
            "github_link",
            "linkedin_link",
            "team",
            "question_1_response",
            "question_2_response",
        ]
        self.requestJSON = requestJSON

    def apply(self):
        try:
            ref = db.reference("/core/")
            _id = self.requestJSON["umass_email"].replace("@umass.edu", "").lower()
            for field in self.expectedFields:
                ref.child(_id).child(field).set(self.requestJSON[field])
            ref.child(_id).child("applied_on").set(self.getTime())
            return {
                "status": "success",
                "code": 200,
                "message": "Candidate applied successfully",
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
                "message": "Server failed to process candidate application",
            }

    def validate(self):
        ref = db.reference("/core/")
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
                    "message": "Candidate already applied",
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
