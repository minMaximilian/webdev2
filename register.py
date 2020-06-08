#!/usr/bin/python3

import os
import sys

restricted = "restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
from html import escape
import pymysql as db
import os
import hashlib
import random
import passwords
import funcs
import smtplib

result = ""
form_data = FieldStorage()
uname = form_data.getfirst("uname")
pwd = form_data.getfirst("pwd")
cpwd = form_data.getfirst("cpwd")
mail = form_data.getfirst("mail")

# escape
if uname:
    uname = escape(uname, quote=False)
else:
    uname = ""
if mail:
    mail = escape(mail, quote=False)
else:
    mail = ""
if pwd:
    pwd = escape(pwd, quote=False)
if cpwd:
    cpwd = escape(pwd, quote= False)

def send_confirmation(mail, confirm): # sends an email with the confirmation link
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(passwords.email, passwords.epwd)
    body = "https://cs1.ucc.ie/~sh29/cgi-bin/lab7/confirmation.py?confirmUrl=" + confirm
    body_mail = """
    From: %s 
    To: %s
    Subject: Account Confirmation

    %s

    This is an automated message do not reply to this email
    """ % (passwords.email, mail, body)
    server.sendmail(passwords.email, mail, body_mail)
    server.close()     

def check_uname(uname): # checks if there is a unique name
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname
                    FROM users
                    WHERE uname = %s""", (uname))
    for row in cursor.fetchall():
        if uname == row["uname"]:
            connection.commit()
            cursor.close()
            connection.close()
            return False
    connection.commit()
    cursor.close()
    connection.close()
    return True

def init_elo(uname): # checks if there is a unique name
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""INSERT INTO elo VALUES (%s, 1000, 0)""", (uname))
    connection.commit()
    cursor.close()
    connection.close()

def check_mail(mail): # checks if the mail is already registered
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT mail
                    FROM users
                    WHERE mail = %s""", (mail))
    for row in cursor.fetchall():
        if mail == row["mail"]:
            connection.commit()
            cursor.close()
            connection.close()
            return False
    connection.commit()
    cursor.close()
    connection.close()
    return True

try:
    if not(uname and pwd and cpwd and mail):
        if uname or pwd or cpwd or mail:
            result += "Please fill in all the given fields."
            
    else:
        if check_uname(uname) and pwd == cpwd and check_mail(mail):
            salt = funcs.generate_string(8)
            new_pwd = pwd + salt
            sha_pwd = hashlib.sha256(new_pwd.encode()).hexdigest()
            confirmUrl = funcs.generate_string(32)
            send_confirmation(mail, confirmUrl)
            connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
            cursor = connection.cursor(db.cursors.DictCursor)
            cursor.execute("""INSERT INTO users (uname, mail, pwd, salt, confirm, confirmUrl) VALUES (%s, %s, %s, %s, %s, %s)""", (uname, mail, sha_pwd, salt, 0, confirmUrl))
            connection.commit()
            cursor.close()
            connection.close()
            init_elo(uname)
            funcs.redirect("check_mail.html")
            
        if not(pwd == cpwd):
            result += "The passwords do not match."
        else:
            result += "User or e-mail already registered in the system. "
except:
    result += "Email was invalid, or something else incredibly wrong has just happened. "

finally:
    print("Content-Type: text/html")
    print()
    print("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <title>Registry</title>
                <link rel="stylesheet" href="css/index.css" />
                <script src="register.js" type="module"></script>
            </head>
            <body>
            <header>
                <a href="index.py">Nice Chess Games</a>
                <div
                    ><a href="home/leaderboard.py">Leaderboard</a
                    ><a href="">Search</a
                    ><a href="login.py">Login</a
                ></div>
            </header>
            <section class="form-wrapper">
                <form action="register.py" method="post">
                    <label for="mail">E-mail:</label>
                    <input type="text" id="mail" name="mail" value="%s">
                    <label for="uname">Username:</label>
                    <input type="text" id="uname" name="uname" value="%s">
                    <label for="pwd">Password:</label>
                    <input type="password" id="pwd" name="pwd">
                    <label for="cpwd">Confirm Password:</label>
                    <input type="password" id="cpwd" name="cpwd">
                    <button type="submit"> Register </button>
                    <p>%s</p>
                </form>
            </section>
            </body>
            </html>""" % (mail, uname, result))