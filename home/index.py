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

def retrieve_incoming(uname):
    txt = "<section><h2 class=\"incoming\"> In coming game requests</h2>"
    txt_2 = ""
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_1, game_id FROM chess_games WHERE player_2 = %s AND confirmed = 0 AND win = 0""", (uname))
    for row in cursor.fetchall():
        txt_2 += ("""<form class="game-request" action="../game/mm_handler.py" method="post">
        Game request from %s:
        <button name="accept" type="submit" id="accept" value="%s"> Accept </button>
        <button name="decline" type="submit" id="decline" value="%s"> Decline </button>
        </form>""" % (row["player_1"], row["game_id"], row["game_id"]))
    if txt_2 == "":
        txt += "<p> No game requests from other players!</p>"
    txt += txt_2
    txt += "</section>"
    return txt

def retrieve_outgoing(uname):
    txt = "<section><h2 class=\"outgoing\"> Out going game requests</h2>"
    txt_2 = ""
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_2, game_id FROM chess_games WHERE player_1 = %s AND confirmed = 0 AND win = 0""", (uname))
    for row in cursor.fetchall():
        txt_2 += ("""<form class="game-request" action="../game/mm_handler.py" method="post">
        Game request to %s:
        <button name="cancel" type="submit" id="cancel" value="%s"> Cancel </button>
        </form>""" % (row["player_2"], row["game_id"]))
    if txt_2 == "":
        txt += "<p> No game requests to other players!</p>"
    txt += txt_2
    txt += "</section>"
    return txt


def challenge(uname):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname
                    FROM users
                    WHERE uname = """, (uname))
    for row in cursor.fetchall():
            connection.commit()
            cursor.close()
            connection.close()
            return row["uname"]
    cursor.close()
    connection.close()

def retrieve_elo(uname):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT elo, numgames FROM elo WHERE uname = %s""", (uname))
    row = cursor.fetchone()
    txt = ("<p> You have achieved an ELO of %s over the course of %s games" % (row["elo"], row["numgames"]))
    connection.commit()
    cursor.close()
    connection.close()
    return txt

def retrieve_stats(uname):
    txt = "<section><h2 class=\"game-history\"> Game History </h2>"
    txt_2 = ""
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_1, player_2, win FROM chess_games WHERE (player_1 = %s OR player_2 = %s) AND confirmed = 1 AND win != 0""", (uname, uname))
    for row in cursor.fetchall():
        if row["player_1"] == uname and row["win"] == 1:
            txt_2 += ("<p> You have won against %s </p>" % (row["player_2"]))

        elif row["player_2"] == uname and row["win"] == 2:
            txt_2 += ("<p> You have won against %s </p>" % (row["player_1"]))

        else:
            if uname == row["player_1"]:
                txt_2 += ("<p> You have lost against %s </p>" % (row["player_2"]))
            else:
                txt_2 += ("<p> You have lost against %s </p>" % (row["player_1"]))

    if txt_2 == "":
        txt += "<p> No past games </p>"
    txt += txt_2
    txt += "</section>"
    return txt


result = ""
result_2 = ""
incoming = "No incoming requests to play games"
outgoing = "No outgoing requests to play games"
form = """<form class="find-opponent" action="index.py" method="post">
            <label for="opponent"> Who do you want to challenge today?</label>
            <input type="text" id="opponent" name="opponent" value="">
            <button type="submit"> Throw the gauntlet </button>
            <p>%s</p>
        </form>"""

form_data = FieldStorage()
opponent = form_data.getfirst("opponent")
cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            uname = funcs.return_uname(cookie["sessionId"].value)
            if opponent and not(opponent == uname):
                opponent = escape(opponent, quote=False)
                if funcs.check_if_exists_uname(opponent):
                    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
                    cursor = connection.cursor(db.cursors.DictCursor)
                    cursor.execute("""INSERT INTO chess_games (player_1, player_2, confirmed, win) VALUES (%s, %s, 0, 0)""", (uname, opponent))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    form = (form % ("Succesful request!"))
                else:
                    form = (form % ("The user doesn't exist or hasn't confirmed their account"))
            else:
                form = (form % (""))

            if funcs.is_ongoing_game(uname):
                result = ("""<form class="game-request" action="../game/mm_handler.py" method="post">
                                Concurrently in a game:
                                <button name="continue" type="submit" id="continue" value="%s"> Continue </button>
                                <button name="forfeit" type="submit" id="forfeit" value="%s"> Forfeit </button>
                            </form>""" % (funcs.is_ongoing_game(uname)[1], funcs.is_ongoing_game(uname)[1]))

            else:
                result += form
                result += retrieve_incoming(uname)
                result += retrieve_outgoing(uname)
                result_2 = retrieve_stats(uname)
                
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
                            ><a href="leaderboard.py">Leaderboard</a
                            ><a href="search.py">Search</a
                            ><a href="logout.py">Logout</a
                        ></div>
                    </header>
                    <section class="user-content">
                        <section class="requests">
                        <p> Hello %s, fancy a game? Look up a user in the search and challenge them using the form below! Or you can accept an already incoming request</p>
                        %s
                        </section>
                        <section class="history">
                        %s
                        Here is a history of games you've played
                        %s
                        </section>
                    </section>
                    </body>
                </html>""" % (uname, result, retrieve_elo(uname), result_2))
        else:
            funcs.redirect("login.py")

    except Exception as E:
        funcs.redirect("login.py")

else:
    funcs.redirect("login.py")