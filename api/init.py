import firebase_admin
from dotenv import load_dotenv
import os
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message

from api.user_registration import UserRegistration
from api.user_decision import UserDecision
from api.user_attendance import UserAttendance

load_dotenv()

cred_object = firebase_admin.credentials.Certificate(
    {
        "type": os.environ.get("FIREBASE_TYPE"),
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
        "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL"
        ),
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
    }
)

default_app = firebase_admin.initialize_app(
    cred_object, {"databaseURL": os.environ.get("DATABASE_URL"),}
)

app = Flask(__name__)
CORS(app)
app.config.update(
    {
        "MAIL_SERVER": os.environ.get("MAIL_SERVER"),
        "MAIL_PORT": os.environ.get("MAIL_PORT"),
        "MAIL_USERNAME": os.environ.get("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.environ.get("MAIL_PASSWORD"),
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
    }
)
mail = Mail(app)

"""Display a message welcoming the user/tester at endpoint: "https://cicsoft-web-api.herokuapp.com/"

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


"""Register a new user in the database at endpoint: "https://cicsoft-web-api.herokuapp.com/user-registration"

Returns:
    response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
"""

@app.route("/user-decision", methods=["POST"])
def decideUser():
    userDecision = UserDecision(request.get_json())
    decision = userDecision.decide()
    if decision["status"] == "success":
        for accepted in decision["data"]["accepted"]:
            msg = Message(
                subject="Congratulations! Welcome to CICSoft!",
                sender=("CICSoft", os.environ.get("MAIL_USERNAME")),
                recipients=[accepted["umassEmail"]],
            )
            msg.html = render_template(
                "acceptance.html", firstName=accepted["firstName"], lastName=accepted["lastName"]
            )
            mail.send(msg)
        # for rejected in decision["data"]["rejected"]:
        # ! TO BE DONE SOON
        return {"message": decision["message"]}, decision["code"]
    else:
        return {"message": decision["message"]}, decision["code"]

@app.route("/user-registration", methods=["POST"])
def registerUser():
    userRegistration = UserRegistration(request.get_json())
    validation = userRegistration.validate()
    if validation["status"] == "success":
        registration = userRegistration.register()
        if registration["code"] == 200:
            firstName = registration["data"]["first_name"]
            lastName = registration["data"]["last_name"]
            umassEmail = registration["data"]["umass_email"]
            msg = Message(
                subject="We have received your application for CICSoft!",
                sender=("CICSoft", os.environ.get("MAIL_USERNAME")),
                recipients=[umassEmail],
            )
            msg.html = render_template(
                "welcome.html", firstName=firstName
            )
            mail.send(msg)
            msg_self = Message(
                subject=f"{firstName} {lastName} has applied to be a member!",
                sender=("CICSoft", os.environ.get("MAIL_USERNAME")),
                recipients=['cicsoftumass@gmail.com'],
            )
            msg_self.html = render_template(
                "registration_notification.html", firstName=firstName, lastName=lastName, umassEmail=umassEmail
            )
            mail.send(msg_self)
        return {"message": registration["message"]}, registration["code"]
    else:
        return {"message": validation["message"]}, validation["code"]