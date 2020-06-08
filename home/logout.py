#!/usr/bin/python3

import cgi

import os
import sys

restricted = "../restricted"
sys.path.append(os.path.abspath(restricted))

import passwords
import funcs

from os import environ
from http.cookies import SimpleCookie

import pymysql as db

cookie = SimpleCookie()
http_cookie_header = environ.get("HTTP_COOKIE")

if http_cookie_header:
    cookie.load(http_cookie_header)
    try:
        if funcs.check_if_exists(cookie["sessionId"].value):
            connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
            cursor = connection.cursor(db.cursors.DictCursor)
            cursor.execute("""UPDATE users
                            SET sessionId=NULL
                            WHERE sessionId= %s""", (cookie["sessionId"].value))
            connection.commit()
            cursor.close()
            connection.close()
            funcs.redirect("index.py")

        else:
            funcs.redirect("index.py")
    
    except:
        funcs.redirect("index.py")

else:
    funcs.redirect("index.py")