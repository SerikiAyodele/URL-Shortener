Building a URL Shortener to learn system design.

# Stack
Language: python
Frame work: Flask 
--

# Terminologies
- virtual environmnet: Think of it like a container but for only python libraries

--

# Steps
1. Install Flask in a virtual environmnet, it keeps your projects packages separate from your system
    ```
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
    - `pip install flask`  
    ```
    Output
    `Successfully installed blinker-1.9.0 click-8.1.8 flask-3.1.3 importlib-metadata-8.7.1 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 werkzeug-3.1.8 zipp-3.23.1`

2. Run `app.py`
    - `flask --app <filename> run`

--

# Problems with v1 (v1-app.py)
1. Throwing correct error's instead of 500's

2.  line 1; `secret = secrets.token_urlsafe(4)` 
    line 2; `links[secret] = data["url"]`

    *Look at these line:*
    - We generate a random code. We store it. We never check if that code is already taken.
    - If secrets happens to hand us a code that already exists, line 2 overwrites it.
    - Someone's existing short link now points at a stranger's URL. Silently. No error.

    *How many codes can we generate with 4 bytes?*
    ```
    token_urlsafe(4) → 4 random bytes
    4 bytes → 32 bits
    32 bits → 2^32 combinations
    2^32 → 4,294,967,296
    ```
    This number is every code the function can possibly produce.

    *say we have 10m links stored, what are the chances that a generated code is repeated?*
    ```
    (10000000 / 4294967296) = 0.0023283064365386963
    0.0023283064365386963 * 10000000 = 23283.064365386963
    ```
    About 23,000 collisions.
    That is 23,000 links silently pointing at the wrong site without a sinle error from our code.

    ## Design Decision
    Now the design decision. Two options:

    A. Before storing, check if the code is already in links. If it is, generate another. Repeat.

    B. Make the code longer. token_urlsafe(8) instead of 4.

# Problems with v2 (v2-app.py)
1. The dict dies every time the server restarts.
    *soln: persistence. Move links out of memory and into a database*

    ## Designing the DB

2. Requests reading from disk all the time 
   *soln: cacahe*
   Load testing with apache bench without a cache
   `ab -n 1000 -c 10 http://127.0.0.1:5001/YOURCODE`

   #### result
   ```
   816 requests/sec
   p50   12 ms
   p99   16 ms
   max   19 ms
   ```
   ---

Now the useful question: what is taking 12ms?

Two candidates:

- SQLite. Opening a connection and reading from disk on every request.
- Flask's dev server. The thing that prints a warning about not being for production.

You are about to add a cache to speed up the database part. But if the database is not the slow part, the cache will change nothing.

---

So isolate it first.

Add a route back that does no database work at all. Something like /ping that just returns the word "ok".

Then run the same ab against it.

If /ping also gives around 816/s, the database is not your bottleneck. Flask is. A cache would be pointless.

If /ping is much faster, the database really is costing you, and a cache is worth adding.

Measure before you optimise. Write the route and run it.

              req/sec    p50    p99    server think time
/ping           856      12ms   13ms   0ms
/<code>         817      12ms   16ms   1ms

The difference is about 4%.

---

What that tells us:

SQLite is not the bottleneck. Adding a cache would buy us at most 4%, and probably less.