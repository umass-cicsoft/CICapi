import firebase_admin
from dotenv import load_dotenv
import os
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_mail import Mail, Message

from api.user_registration import UserRegistration
from api.user_decision import UserDecision
from api.user_verification import UserVerification
from api.user_attendance import UserAttendance
from api.user_tech_poll import UserTechPoll
from api.lab_ideas import labIdeas


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
        "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
    }
)

default_app = firebase_admin.initialize_app(
    cred_object, {"databaseURL": os.environ.get("DATABASE_URL"), })

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


@app.route("/", methods=["GET"])
def main():
    """Display a message welcoming the user/tester at endpoint: "https://cicsoft-web-api.herokuapp.com/"
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    response = {
        "status": "success",
        "code": 200,
        "message": "Welcome to CICSoft's API! In order to register for Weekly Sessions, please apply through our website at https://umass-cicsoft.github.io.",
    }
    return {"message": response["message"]}, response["code"]


@app.route("/user/register", methods=["POST"])
def registerUser():
    """Register a new user in the database at endpoint: "https://cicsoft-web-api.herokuapp.com/user/register"
    Request Payload: 
        {
            "first_name": <User's first name>,
            "last_name": <User's last name>,
            "umass_email": <User's official @umass.edu email address>,
            "graduation_year": <User's graduation year>,
            "major": <User's major(s)>,
            "github_link": <Link to user's GitHub profile>,
            "linkedin_link": <Link to user's LinkedIn profile>,
            "interest_response": <User's response to why they are interested in us>,
            "referral_response": <User's response to how they got to referred to us>
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    userRegistration = UserRegistration(request.get_json())
    validation = userRegistration.validate()
    if validation["status"] == "success":
        registration = userRegistration.register()
        if registration["code"] == 200:
            firstName = registration["data"]["first_name"]
            lastName = registration["data"]["last_name"]
            sendEmail(
                "We have received your application for CICSoft!", "welcome.html", registration[
                    "data"],
            )
            sendEmail(
                f"{firstName} {lastName} has applied to be a member!",
                "registration_notification.html",
                registration["data"],
                "cicsoftumass@gmail.com",
            )
        return {"message": registration["message"]}, registration["code"]
    else:
        return {"message": validation["message"]}, validation["code"]


@app.route("/user/decide", methods=["POST"])
def decideUser():
    """Decide on user applications at endpoint: "https://cicsoft-web-api.herokuapp.com/user/decide"
    Request Payload: 
        {
            "accepted": [<Accepted user's official @umass.edu email address>, ...],
            "waitlisted": [<Waitlisted user's official @umass.edu email address>, ...]
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    decision = UserDecision(request.get_json()).decide()
    if decision["status"] == "success":
        for accepted in decision["data"]["accepted"]:
            sendEmail("Congratulations! Welcome to CICSoft!",
                      "acceptance.html", accepted)
        for waitlisted in decision["data"]["waitlisted"]:
            sendEmail("Thank you for applying to CICSoft!",
                      "waitlist.html", waitlisted)
    return {"message": decision["message"]}, decision["code"]


@app.route("/user/verify", methods=["POST"])
def verifyUser():
    """Verify a user's request to become a Discord "Member" at endpoint: "https://cicsoft-web-api.herokuapp.com/user/verify"
    Request Payload: 
        {
            "umass_email": <User's official @umass.edu email address>,
            "otp": <OTP to be used for verification purposes>
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    verification = UserVerification(request.get_json()).verify()
    if verification["status"] == "success":
        otp = verification["data"]["otp"]
        sendEmail(
            f"CICSoft Verification Code: {otp}", "verification.html", verification["data"],
        )
    return {"message": verification["message"], "discord_id": verification["discord_id"]}, verification["code"]


@app.route("/user/verified", methods=["POST"])
def updateVerifiedUser():
    """Update a user's discord_id if verified at endpoint: "https://cicsoft-web-api.herokuapp.com/user/verified"
    Request Payload: 
        {
            "umass_email": <User's official @umass.edu email address>,
            "discord_id": <User's Discord identifier>
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    verified = UserVerification(request.get_json()).updateVerified()
    return {"message": verified["message"]}, verified["code"]


@app.route("/technology_poll", methods=["POST"])
def pollTechnologySubmission():
    """Add technology poll submission in the database at endpoint: "https://cicsoft-web-api.herokuapp.com/technology_poll"
    Request Payload: 
        {
            "poll_value": <User's poll choice>
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    techPoll = UserTechPoll(request.get_json(), request).poll()
    return {"message": techPoll["message"]}, techPoll["code"]


@app.route("/lab_Ideas", methods=["POST"])
def labIdeaSubmission():
    """Add idea for the lab in the database at endpoint: "https://cicsoft-web-api.herokuapp.com/lab_ideas"
    Request Payload: 
        {
            "first_name": <User's first name>,
            "last_name": <User's last name>,
            "idea_text": <User's lab idea>
        }
    Returns:
        response: a 2-tuple containing an object (with only a message attribute) and an HTTP response code
    """
    labIdea = labIdeas(request.get_json(), request).idea()
    return {"message": labIdea["message"]}, labIdea["code"]


def sendEmail(subject, htmlTemplate, params, recipient=None):
    """Send an email to appropriate recipient with given template and parameters
    """
    if recipient is None:
        recipient = params.get("umass_email")
    msg = Message(subject=subject, sender=(
        "CICSoft", os.environ.get("MAIL_USERNAME")), recipients=[recipient],)
    msg.html = render_template(
        htmlTemplate,
        firstName=params.get("first_name"),
        lastName=params.get("last_name"),
        umassEmail=params.get("umass_email"),
        otp=params.get("otp"),
    )
    mail.send(msg)
