from firebase_admin import db


class UserVerification:
    def __init__(self, requestJSON):
        self.requestJSON = requestJSON

    def verify(self):
        try:
            members = dict(db.reference("/members/").get())
            _id = self.requestJSON["umass_email"].replace("@umass.edu", "")
            if _id in members.keys() and members.get(_id).get("status") == "member":
                return {
                    "status": "success",
                    "code": 200,
                    "message": "Successfully sent verification code to member!",
                    "data": {
                        "first_name": members.get(_id).get("first_name"),
                        "last_name": members.get(_id).get("last_name"),
                        "umass_email": self.requestJSON["umass_email"],
                        "otp": self.requestJSON["otp"],
                    },
                }
            else:
                return {
                    "status": "error",
                    "code": 404,
                    "message": "No member with given email address",
                }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process user verification",
            }

    def updateVerified(self):
        try:
            ref = db.reference("/members/")
            _id = self.requestJSON["umass_email"].replace("@umass.edu", "").lower()
            ref.child(_id).child("discord_id").set(self.requestJSON["discord_id"])
            return {
                "status": "success",
                "code": 200,
                "message": "Verified member's details successfully updated!",
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process verified user's details",
            }