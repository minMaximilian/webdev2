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

from html import escape

form_data = FieldStorage()
cookie = form_data.getfirst("cookie")

def render(board):
    result = "<table class=\"board\"><tr>"
    y = 1
    x = "a"
    for rows in range(9):
        if rows == 0:
            for i in range(9):
                if i == 8:
                    x = chr(x_i)
                    result += "<th scope=\"col\" class=\"x\"> %s </th></tr>" % (x)
                elif i > 0:
                    x = chr(x_i)
                    result += "<th scope=\"col\" class=\"x\"> %s </th>" % (x)
                    x_i += 1
                else:
                    x_i = ord(x)
                    result += "<th class=\"xyz\"></th>"
        else:
            result += "<tr><th scope=\"row\" class=\"y\"> %s </th>" % (rows)
            for row in range(8):
                if board[rows - 1][row]:
                    result += "<td> <img src=\"../icons/%s.svg\" alt=\"%s\" /> </td>" % (board[rows - 1][row], board[rows - 1][row])
                else:
                    result += "<td></td>"
            result += "</tr>"
        y += 1
    result += "</table>"
    return result

print("Content-Type: text/plain")
print()

try:
    if funcs.check_if_exists(cookie):
        uname = funcs.return_uname(cookie)
        m = funcs.is_ongoing_game(uname)
        if m:
            session_store = open("session_" + str(m[1]), writeback = True)
            board = session_store["board"]
            result = render(board)   
            session_store.close()
            print(result)

        else:
            print("<p> Game is over what are you doing here! </p>")
except:
    print("error")