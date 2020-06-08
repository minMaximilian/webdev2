#!/usr/bin/python3

import os
import sys

restricted = "restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
import pymysql as db
import passwords
import funcs
import smtplib
import hashlib

form_data = FieldStorage()
mail = form_data.getfirst("mail")

result = ""

def check_if_mail_exists(mail):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT mail, confirm, salt
                    FROM users
                    WHERE mail = %s""", (mail))
    for row in cursor.fetchall():
        if mail == row["mail"] and row["confirm"] == 1:
            salt = row["salt"]
            connection.commit()
            cursor.close()
            connection.close()
            return True, salt
    connection.commit()
    cursor.close()
    connection.close()
    return False, "Dummy String"

def send_pwd(mail, pwd): # sends an email with the confirmation link
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(passwords.email, passwords.epwd)
    body = "Your new password is " + pwd + " use this for any future logins till I implement a nicer system to allow the user to change their passwords"
    body_mail = """
    From: %s 
    To: %s
    Subject: Account Confirmation

    %s

    This is an automated message do not reply to this email
    """ % (passwords.email, mail, body)
    server.sendmail(passwords.email, mail, body_mail)
    server.close()     

try:
    if mail:
        check = check_if_mail_exists(mail)
        if check[0]:
            result = "You got mail"
            pwd = funcs.generate_string(8)
            new_pwd = pwd + check[1]
            sha_pwd = hashlib.sha256(new_pwd.encode()).hexdigest()
            connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
            cursor = connection.cursor(db.cursors.DictCursor)
            cursor.execute("""UPDATE users SET pwd = %s WHERE mail = %s""", (sha_pwd, mail))
            connection.commit()
            cursor.close()
            connection.close()
            send_pwd(mail, pwd)

        else:
            result = "Mail doesn't exist or hasn't been confirmed in the system"
    else:
        mail = ""

except:
    result = "error"

finally:
    print("Content-Type: text/html")
    print()
    print("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <title>Forgot your password?</title>
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
                <form action="forgot.py" method="post">
                    <label for="mail">E-mail:</label>
                    <input type="text" id="mail" name="mail" value="%s">
                    <button type="submit"> Send </button>
                    <p>%s</p>
                </form>
            </section>
            </body>
            </html>""" % (mail, result))
    