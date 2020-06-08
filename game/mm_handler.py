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
import math

from os import environ
from http.cookies import SimpleCookie

def handle_request(gid, player, num):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_%s
                    FROM chess_games
                    WHERE game_id = %s AND confirmed = 0 AND win = 0""", (num, gid))
    for row in cursor.fetchall():
        if player == row["player_" + str(num)]:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    connection.commit()
    cursor.close()
    connection.close()
    return False

def handle_forfeit(gid, player):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_1, player_2
                    FROM chess_games
                    WHERE game_id = %s AND confirmed = 1 AND win = 0""", (gid))
    for row in cursor.fetchall():
        if player == row["player_1"]:
            connection.commit()
            cursor.close()
            connection.close()
            return True, row["player_2"]

        elif player == row["player_2"]:
            connection.commit()
            cursor.close()
            connection.close()
            return True, row["player_1"]
    connection.commit()
    cursor.close()
    connection.close()
    return False, "dummy text"

def update_elo(uname, opponent, boolean):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname, elo
                    FROM elo
                    WHERE uname = %s or uname = %s""", (uname, opponent))
    for row in cursor.fetchall():
        if uname == row["uname"]:
            player_1_elo = row["elo"]
        else:
            player_2_elo = row["elo"]

    if boolean:
        S_a = 1
        S_b = 0
    else: 
        S_b = 1
        S_a = 0

    R_a = round(player_1_elo + (32*(S_a - (1/(1+10**((player_2_elo - player_1_elo)/400))))))
    R_b = round(player_2_elo + (32*(S_b - (1/(1+10**((player_1_elo - player_2_elo)/400))))))

    cursor.execute("""UPDATE elo SET elo = %s, numgames = numgames + 1 WHERE uname = %s""", (R_a, uname))
    connection.commit()
    cursor.execute("""UPDATE elo SET elo = %s, numgames = numgames + 1 WHERE uname = %s""", (R_b, opponent))
    connection.commit()
    cursor.close()
    connection.close()

def close_session(gid, uname, boolean):
    p = player_names(gid)
    if p[0] == uname:
        if boolean:
            win = 1
        else:
            win = 2
    else:
        if boolean:
            win = 2
        else:
            win = 1

    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""UPDATE chess_games SET win = %s WHERE game_id = %s""", (win, gid))
    connection.commit()
    cursor.close()
    connection.close()

def player_names(gid):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_1, player_2
                    FROM chess_games
                    WHERE game_id = %s""", (gid))
    for row in cursor.fetchall():
        connection.commit()
        cursor.close()
        connection.close()
        return row["player_1"], row["player_2"]

def request_response(gid, boolean=False):
    if boolean:
        connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
        cursor = connection.cursor(db.cursors.DictCursor)
        cursor.execute("""UPDATE chess_games SET confirmed = 1 WHERE game_id = %s""", (gid))
        connection.commit()
        cursor.close()
        connection.close()
    else:
        connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
        cursor = connection.cursor(db.cursors.DictCursor)
        cursor.execute("""DELETE FROM chess_games WHERE game_id = %s""", (gid))
        connection.commit()
        cursor.close()
        connection.close()

form_data = FieldStorage()

accept = form_data.getfirst("accept")
decline = form_data.getfirst("decline")
cancel = form_data.getfirst("cancel")
forfeit = form_data.getfirst("forfeit")
cont = form_data.getfirst("continue")

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            uname = funcs.return_uname(cookie["sessionId"].value)
            if accept:
                accept = escape(accept)
                if handle_request(accept, uname, 2):
                    request_response(accept, True)
                    players = list(player_names(accept))
                    session_store = open("session_" + str(accept), writeback = True)
                    random.shuffle(players)
                    session_store["white"] = players[0]
                    session_store["black"] = players[1]
                    session_store["turn"] = True
                    session_store["board"] = [["wr", "wh", "wb", "wq", "wk", "wb", "wh", "wr"], ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["", "", "", "", "", "", "", ""], ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"], ["br", "bh", "bb", "bq", "bk", "bb", "bh", "br"]]
                    session_store.close()
                    redirect("game/chess.py")

                else:
                    funcs.redirect("home/index.py")

            elif decline:
                decline = escape(decline)
                if handle_request(decline, uname, 2):
                    request_response(decline)
                    funcs.redirect("home/index.py")
                else:
                    funcs.redirect("home/index.py")

            elif cancel:
                cancel = escape(cancel)
                if handle_request(cancel, uname, 1):
                    request_response(cancel)
                    funcs.redirect("home/index.py")
                else:
                    funcs.redirect("home/index.py")
            
            elif forfeit:
                forfeit = escape(forfeit)
                fr = handle_forfeit(forfeit, uname)
                if fr[0]:
                    update_elo(uname, fr[1], False)
                    close_session(forfeit, uname, False)
                    funcs.redirect("home/index.py")

                else:
                    funcs.redirect("home/index.py")
            
            elif cont:
                funcs.redirect("game/chess.py")

            else:
                funcs.redirect("home/index.py")

        else:
            funcs.redirect("login.py")

    except Exception as E:
        funcs.redirect("home/index.py")

else:
    funcs.redirect("login.py")