URL Shortener

=============

Stack

-----

* Language: python
* Frame work: Flask 
* Database: MySQL

Terminologies
-------------

*   Virtual environmnet: Think of it like a container but for only python libraries



Try it out
==========

[X] 1. Install Flask in a virtual environmnet, it keeps your        projects packages separate from your system
    ```
    `python3 -m venv .venv`
    `source .venv/bin/activate`
    `pip install flask`  
    ```
    Output
    ```
    Successfully installed blinker-1.9.0 click-8.1.8 flask-3.1.3 importlib-metadata-8.7.1 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 werkzeug-3.1.8 zipp-3.23.1
    ```

[X] 2. Run
      `flask --app <filename> run`



Problems with v1 (v1-app.py)
==============================

*   Throwing incorrect error's instead of 500's
    Solution
    --------

*   line 1; `secret = secrets.token_urlsafe(4)` 
    line 2; `links[secret] = data["url"]`

    Look at these lines
    -------------------
    *   We generate a random code of 4 bytes. We store it. We never check if that code is already taken.
    *   If secrets happens to hand us a code that already exists, line 2 overwrites it.
    *   Someone's existing short link now points at a stranger's URL with no error.

    The math: How many codes can we generate with 4 bytes?
    ------------------------------------------------------

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

    Solution
    ---------
    Now the design decision. Two options:

    A. Before storing, check if the code is already in links. If it is, generate another. Repeat.
    We go with this 

    B. Make the code longer. token_urlsafe(8) instead of 4.
    This defeats the goal of having short codes


Problems with v2 (v2-app.py)
============================

*   The dict dies every time the server restarts.
    soln: *persistence.* Move links out of memory and into a database

    Guiding questions to designing the DB
    --------------------------------------

*   Requests reading from disk all the time 

    Two candidate fixes: add a cache, or change the server.
    Measure before picking.

    Baseline (Flask dev server)
    ---------------------------
    `ab -n 1000 -c 10 http://127.0.0.1:5001/YOURCODE`

        816 req/sec   p50 12ms   p99 16ms

    What is taking 12ms? SQLite, or the dev server?

    Isolate it
    ----------
    Add a route that touches no database:

        ```
        @app.route("/ping")
        def ping():
            return "ok"
        ```
    If /ping is also ~816/s, the database is not the bottleneck.

                    req/sec    p50     think time
        /ping         856      12ms    0ms
        /<code>       817      12ms    1ms

    4% difference. **SQLite is not the bottleneck. The dev server is.**
    A cache here would buy almost nothing.

    Fix: swap the server
    --------------------
        ```
        pip install gunicorn
        gunicorn -w 4 'v3-app:app' -b 127.0.0.1:5001

                    req/sec    p50     per request
        /ping        7837      1ms     1.28ms
        /<code>      6670      1ms     1.50ms
        ```

    **9x faster.** The dev server was the whole problem.
    Not one line of app.py changed. WSGI is a standard, so servers swap freely.

    Cache decision
    --------------
    Database now costs 0.22ms, about 15% of the request.

    **No cache.** 15% is not worth another service to run and break.

    Revisit after Postgres: that lookup goes over the network, so it
    becomes milliseconds instead of 0.22ms. Then a cache earns its place.

    Learn: what "slow" means
    ------------------------
    12ms is fine for one user. The problem is throughput.
    11ms per request means one worker caps at ~90/sec.
    900/sec would need 10x the machines, for work that should be free.

        read from memory       0.0001 ms
        read from SSD          0.1 ms
        database lookup        1 ms
        network, same city     1 ms
        network, Lagos to US   150 ms

    /ping does nothing and cost 11ms. That is 99% overhead.

    Slow is relative to what the work requires, not to a second.
    150ms across continents is fine. 11ms to return "ok" locally is not.

    Rule: fix the biggest bottleneck and the next one becomes visible.



Communication and Support
=========================

* Mailing Lists: https://lore.kernel.org/
* IRC: #kernelnewbies on irc.oftc.net
* Bugzilla: https://bugzilla.kernel.org/
* MAINTAINERS file: Lists subsystem maintainers and mailing lists
* Email Clients: Documentation/process/email-clients.rst