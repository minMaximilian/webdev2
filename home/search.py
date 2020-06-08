#!/usr/bin/python3

import os
import sys

restricted = "../restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
from html import escape
import pymysql as db
import passwords
import funcs

from os import environ
from http.cookies import SimpleCookie

result = ""

form_data = FieldStorage()
request = form_data.getfirst("search")

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

result_2 = "href=\"../login.py\">Login"

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            result_2 = "href=\"index.py\">Home"

    except:
        pass

try:
    if request:
        request = escape(request, quote=False)
        connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
        cursor = connection.cursor(db.cursors.DictCursor)
        cursor.execute("""SELECT uname
                        FROM users
                        WHERE confirm = 1 AND uname = %s
                        LIMIT 20
                        """, (request))
        result = "<table><tr><th>Username</th></tr>"
        for row in cursor.fetchall():
            result += "<tr><td><a href=\"\">%s</a></td></tr>" % (row["uname"])
        result += "</table>"
        connection.commit()
        cursor.close()
        connection.close()
except:
    result = "Search Failed"

print("Content-Type: text/html")
print()        
print("""
    <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Leaderboard</title>
                <link rel="stylesheet" href="../css/index.css" />
            </head>
            <body>
            <header>
                <a href="../index.py">Nice Chess Games</a>
                <div
                    ><a href="leaderboard.py">Leaderboard</a
                    ><a href="">Search</a
                    ><a %s </a
                ></div>
            </header>
            <section class="form-wrapper">
                <form class="search" action="search.py" method="post">
                    <input type="text" id="search" name="search">
                    <button type="submit"> Search </button>
                </form>
                %s
            </section>
            </body>
            </html>""" % (result_2, result))
