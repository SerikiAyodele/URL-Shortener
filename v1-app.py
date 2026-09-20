from flask import Flask
from flask import request
from flask import redirect
from flask import abort
import secrets

app = Flask(__name__)
links = {}

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    secret = secrets.token_urlsafe(4)
    links[secret] = data["url"]
    return secret

@app.route("/<code>")
def get_code(code):
    long = links[code] 
    return redirect(long)
