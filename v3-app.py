from flask import Flask
from flask import request
from flask import redirect
from flask import abort
import secrets
import sqlite3

app = Flask(__name__)

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()

    # 1a. reject the request if the url field is missing
    if "url" in data:
        
        #open a connection
        conn = sqlite3.connect("links.db")

        while True:
            code = secrets.token_urlsafe(4)
            try:
                conn.execute("INSERT INTO links VALUES (?, ?)", (code, data["url"]))
                conn.commit()
                break
            except sqlite3.IntegrityError:
                pass
        conn.close()
        return code
    else:
        abort(400)


@app.route("/<code>")
def get_code(code):
    conn = sqlite3.connect("links.db")

    row = conn.execute("SELECT long_url FROM links WHERE code = ?", (code,)).fetchone()
    conn.close()

    if row is None:
        return abort(404)
    else:
        row = row[0]
        return redirect(row)
        

@app.route("/ping")
def ping():
    return "ok"