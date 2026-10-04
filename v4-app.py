from flask import Flask
from flask import request
from flask import redirect
from flask import abort
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
import secrets
import psycopg
import redis
import os

load_dotenv()

app = Flask(__name__)
pool = ConnectionPool(os.environ["DATABASE_URL"])
cache = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()

    # 1a. reject the request if the url field is missing
    if "url" in data:
        
        #open a connection
        with pool.connection() as conn:

            while True:
                code = secrets.token_urlsafe(4)
                try:
                    conn.execute("INSERT INTO links VALUES (%s, %s)", (code, data["url"]))
                    conn.commit()
                    break
                except psycopg.errors.UniqueViolation:
                    conn.rollback()
            return code
    else:
        abort(400)


@app.route("/<code>")
def get_code(code):
    hit = cache.get(code)
    if hit is None:
        with pool.connection() as conn:
            row = conn.execute("SELECT long_url FROM links WHERE code = %s", (code,)).fetchone()

        if row is None:
            return abort(404)
        else:
            row = row[0]
            cache.set(code, row, ex=3600)
            return redirect(row)
    else:
        return redirect(hit)
        

@app.route("/ping")
def ping():
    return "ok"