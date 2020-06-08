#!/usr/bin/python3

import os
import sys

restricted = "restricted"
sys.path.append(os.path.abspath(restricted))

from cgi import FieldStorage
import pymysql as db
import passwords
from html import escape

form_data = FieldStorage()
confirm = form_data.getfirst("confirmUrl")
if not confirm:
    confirm = ""
confirm = escape(confirm, quote=False)

def check_confirmation(confirm):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT confirmUrl
                    FROM users
                    WHERE confirmUrl = %s""", (confirm))
    for row in cursor.fetchall():
        if confirm == row["confirmUrl"]:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    connection.commit()
    cursor.close()
    connection.close()
    return False

if check_confirmation(confirm):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""UPDATE users
                    SET confirm = 1, confirmUrl = NULL
                    WHERE confirmUrl = %s""", (confirm))
    connection.commit()
    cursor.close()
    connection.close()
    print("Content-Type: text/html")
    print()
    print("""<!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="utf-8" />
                    <title>Confirmed</title>
                    <link rel="stylesheet" href="index.css" />
                    <script src="js/redirect.js" type="module"></script>
                </head>
                <body>
                    <section class="confirmation">
                        <p>Your account has been validated you can login now, redirecting in 5 seconds.</p>
                    </section>
                </body>
            </html>""")

else:
    print("Content-Type: text/html")
    print()
    print("""<!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="utf-8" />
                    <title>Confirmed</title>
                    <link rel="stylesheet" href="css/index.css" />
                    <script src="js/redirect.js" type="module"></script>
                </head>
                <body>
                    <section class="confirmation">
                        <p>Woah you aren't supposed to be here, getting rid of you from this premise in 5 seconds</p>
                    </section>
                </body>
            </html>""")