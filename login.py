#!/usr/bin/python3

import cgi

import os
import sys

restricted = "restricted"
sys.path.append(os.path.abspath(restricted))


from cgi import FieldStorage
from html import escape
import pymysql as db
import passwords
import funcs
from os import environ
from http.cookies import SimpleCookie
from time import time
import hashlib

form_data = FieldStorage()

result = ""
check = False

uname = form_data.getfirst("uname")
pwd = form_data.getfirst("pwd")


if uname:
    uname = escape(uname, quote=False)
else:
    uname = ""

if pwd:
    pwd = escape(pwd, quote=False)

def check_login(uname, pwd):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname, pwd, salt, confirm
                    FROM users
                    WHERE uname = %s""", (uname))
    for row in cursor.fetchall():
        new_pwd = pwd + row["salt"]
        sha_pwd = hashlib.sha256(new_pwd.encode()).hexdigest()
        if uname == row["uname"] and sha_pwd == row["pwd"] and row["confirm"] == 1:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    connection.commit()
    cursor.close()
    connection.close()
    return False

def log_sessionId(uname):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    sessionId = hashlib.sha256(repr(str(time()) + uname).encode()).hexdigest()
    cursor.execute("""UPDATE users SET sessionId = %s WHERE uname = %s""", (sessionId, uname))
    connection.commit()
    cursor.close()
    connection.close()
    return sessionId

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

try:
    if uname and pwd:
        if check_login(uname, pwd):
            cookie["sessionId"] = log_sessionId(uname)
            cookie["sessionId"]["expires"] = 157680000
            print(cookie)
            check = True
        else:
            result += "Either the password or username was typed incorrectly."
    elif (uname or pwd) and not(uname and pwd):
        result += "All fields must be filled"

except:
    result += "Something incredibly wrong has happened"

finally:
    if check:
        funcs.redirect("home/index.py")

    elif http_cookie_header:
        cookie.load(http_cookie_header)
        if funcs.check_if_exists(cookie["sessionId"].value):
            funcs.redirect("home/index.py")

        else:
            print("Content-Type: text/html")
            print()        
            print("""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <title>Login</title>
                    <link rel="stylesheet" href="css/index.css" />
                </head>
                <body>
                <header>
                    <a href="index.py">Nice Chess Games</a>
                    <div
                        ><a href="home/leaderboard.py">Leaderboard</a
                        ><a href="home/search.py">Search</a
                        ><a href="">Login</a
                    ></div>
                </header>
                <section class="form-wrapper">
                    <form action="login.py" method="post">
                        <label for="uname">Username:</label>
                        <input type="text" id="uname" name="uname" value="%s">
                        <label for="pwd">Password:</label>
                        <input type="password" id="pwd" name="pwd">
                        <button type="submit"> Login </button>
                        <p>%s</p>
                        <a href="forgot.py"> Forgot your password? </a>
                    </form>
                </section>
                </body>
                </html>""" % (uname, result))

    else:
        print("Content-Type: text/html")
        print()        
        print("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Login</title>
                <link rel="stylesheet" href="css/index.css" />
            </head>
            <body>
            <header>
                <a href="index.py">Nice Chess Games</a>
                <div
                    ><a href="home/leaderboard.py">Leaderboard</a
                    ><a href="home/search.py">Search</a
                    ><a href="">Login</a
                ></div>
            </header>
            <section class="form-wrapper">
                <form action="login.py" method="post">
                    <label for="uname">Username:</label>
                    <input type="text" id="uname" name="uname" value="%s">
                    <label for="pwd">Password:</label>
                    <input type="password" id="pwd" name="pwd">
                    <button type="submit"> Login </button>
                    <p>%s</p>
                </form>
            </section>
            </body>
            </html>""" % (uname, result))