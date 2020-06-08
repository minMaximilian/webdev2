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

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

result = ""

result_2 = "href=\"../login.py\">Login"

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            result_2 = "href=\"index.py\">Home"

    except:
        pass

try:
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname, elo, numgames 
                    FROM elo
                    WHERE uname IN (
                    SELECT uname
                    FROM users
                    WHERE confirm = 1
                    )
                    ORDER BY elo DESC
                    LIMIT 20
                      """)
    result = "<table><tr><th>Username</th><th>ELO score</th><th>Number of Games</th></tr>"
    for row in cursor.fetchall():
        result += "<tr><td>%s</td><td>%i</td><td>%i</td></tr>" % (row["uname"], row["elo"], row["numgames"])
    result += "</table>"
    cursor.close()  
    connection.close()
except db.Error:
    result = "<p>Big problems are happening right now</p>"

print("Content-Type: text/html")
print()        
print("""
    <!DOCTYPE html>
        <html lang="en">
            <head>
                <title>Leaderboard</title>
                <link rel="stylesheet" href="../css/index.css" />
                <meta charset="UTF-8" />
            </head>
            <body>
            <header>
                <a href="../index.py">Nice Chess Games</a>
                <div
                    ><a href="">Leaderboard</a
                    ><a href="search.py">Search</a
                    ><a %s </a
                ></div>
            </header>
            %s
            </body>
            </html>""" % (result_2, result))
