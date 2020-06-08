#!/usr/bin/python3

import os
import sys
from shelve import open

restricted = "../restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
import pymysql as db
import passwords
import funcs

import random
from html import escape

from os import environ
from http.cookies import SimpleCookie

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            uname = funcs.return_uname(cookie["sessionId"].value)
            m = funcs.is_ongoing_game(uname)
            if m:
                print("Content-Type: text/html")
                print()
                print("""
                <!DOCTYPE html>
                    <html lang="en">
                        <head>
                            <title>Chess</title>
                            <link rel="stylesheet" href="../css/chess.css" />
                            <meta charset="UTF-8" />
                            <script src="../js/chess.js" type="module"></script>
                        </head>
                        <body>
                        <header>
                            <a href="../index.py">Nice Chess Games</a>
                            <div
                                ><a href="../home/leaderboard.py">Leaderboard</a
                                ><a href="../home/search.py">Search</a
                                ><a href="../home/logout.py">Logout</a
                            ></div>
                        </header>
                        <body>
                        <section id="game-wrapper">
                            <section id="chess">
                            </section>
                            <section id="user-control">
                                <article>
                                    <p id="instructions">
                                    The move syntax is "LNLN", where L represents the x-cordinate and N represents the y-cordinate, first "LN" represents the move piece from and second "LN" is move piece to. The game doesn't check for checkmates cause it's computationally intensive to check every path, and also due to lack of websockets.
                                    </p>
                                </article>
                                <p id="error"></p>
                                <textarea id="input"></textarea>
                            </section>
                        </section>
                        </body>
                    </html>""")

            else:   
                funcs.redirect("home/index.py")

        else:
            funcs.redirect("login.py")

    except Exception as E:
        print("Content-Type: text/html")
        print()
        print(E)
        # funcs.redirect("home/index.py")

else:
    funcs.redirect("login.py")