import pymysql as db
import passwords
import random

def check_if_exists(cookie):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT sessionId
                    FROM users
                    WHERE sessionId = %s""", (cookie))
    for row in cursor.fetchall():
        if cookie == row["sessionId"]:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    connection.commit()
    cursor.close()
    connection.close()
    return False

def check_if_exists_uname(uname):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname
                    FROM users
                    WHERE uname = %s AND confirm = 1""", (uname))
    for row in cursor.fetchall():
        if uname == row["uname"]:
            connection.commit()
            cursor.close()
            connection.close()
            return True
    connection.commit()
    cursor.close()
    connection.close()
    return False

def return_uname(cookie):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT uname
                    FROM users
                    WHERE sessionId = %s""", (cookie))
    for row in cursor.fetchall():
        connection.commit()
        cursor.close()
        connection.close()
        return row["uname"]
    connection.commit()
    cursor.close()
    connection.close()
    
def is_ongoing_game(uname):
    connection = db.connect(passwords.serverip, passwords.servername, passwords.serverpass, passwords.db_name)
    cursor = connection.cursor(db.cursors.DictCursor)
    cursor.execute("""SELECT player_1, player_2, game_id
                    FROM chess_games
                    WHERE (player_1 = %s OR player_2 = %s) AND confirmed = 1 AND win = 0""", (uname, uname))
    if cursor.rowcount > 0:
        for row in cursor.fetchall():
            if uname == row["player_1"] or uname == row["player_2"]:
                cursor.close()
                connection.close()
                return True, row["game_id"]
    cursor.close()
    connection.close()
    return False    
    
def redirect(link):
    # Absolute redirect
    print("Content-Type: text/html")
    print()
    print("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta http-equiv="refresh" content="0; URL=https://cs1.ucc.ie/~sh29/cgi-bin/lab7/%s" />
            </head>
            </html>""" % (link)) 

def generate_string(n):
    alp = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([random.choice(alp) for i in range(n)])