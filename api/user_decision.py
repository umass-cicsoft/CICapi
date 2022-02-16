from firebase_admin import db

class UserDecision:
    def __init__(self, requestJSON):
        self.requestJSON = requestJSON
        
    def iterateDecisions(self, emailList, dbRef):
        detailList = list()
        for _id in emailList:
            candidate = dbRef.child("members").child(_id.replace("@umass.edu", ""))
            candidate.child("application_status").set("accepted")
            firstName = str(candidate.child("first_name").get())
            lastName = str(candidate.child("last_name").get())
            umassEmail = str(candidate.child("umass_email").get())
            detailList.append({"firstName": firstName, "lastName": lastName, "umassEmail": umassEmail})
        return detailList
    
    def decide(self):
        try:
            ref = db.reference("/")
            accepted = self.iterateDecisions(self.requestJSON["accepted"], ref)
            rejected = self.iterateDecisions(self.requestJSON["rejected"], ref)
            return {
                "status": "success",
                "code": 200,
                "message": "Members successfully decided!",
                "data": {
                    "accepted": accepted,
                    "rejected": rejected,
                },
            }
        except:
            return {
                "status": "error",
                "code": 500,
                "message": "Server failed to process user decisions",
            }