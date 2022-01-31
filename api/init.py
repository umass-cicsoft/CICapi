import firebase_admin
from dotenv import dotenv_values
from flask import Flask, request
from flask_cors import CORS

from api.user_registration import UserRegistration
from api.user_attendance import UserAttendance

cred_object = firebase_admin.credentials.Certificate(dict(dotenv_values("firebase-keys.env")))
default_app = firebase_admin.initialize_app(cred_object, dict(dotenv_values("urls.env")))

app = Flask(__name__)
CORS(app)

"""Display a message welcoming the user/tester at endpoint: "https://domain.ext/"

Returns:
    response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
"""


@app.route("/", methods=["GET"])
def main():
    response = {
        "status": "success",
        "code": 200,
        "message": "Welcome to CICSoft's API! In order to register for Weekly Sessions, please apply through our website at https://umass-cicsoft.github.io.",
    }
    return {"message": response["message"]}, response["code"]


"""Register a new user in the database at endpoint: "https://domain.ext/user-registration"

Returns:
    response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
"""


@app.route("/user-registration", methods=["POST"])
def registerUser():
    userRegistration = UserRegistration(request.get_json())
    validation = userRegistration.validate()
    if validation["status"] == "success":
        registration = userRegistration.register()
        return {"message": registration["message"]}, registration["code"]
    else:
        return {"message": validation["message"]}, validation["code"]
