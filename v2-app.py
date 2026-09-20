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

    # 1a. reject the request if the url field is missing
    if "url" in data:
        code = secrets.token_urlsafe(4)
        # 2. If code exists create another
        while code in links:
            code = secrets.token_urlsafe(4)
        links[code] = data["url"]
        return code
    else:
        abort(400)

@app.route("/<code>")
def get_code(code):

    # 1b. check we have a link stored under this code"
    if code in links:
        long = links[code] 
        return redirect(long)
    else:
        abort(404)
