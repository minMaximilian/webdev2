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
move = form_data.getfirst("move")

def convert_verify(move):
    # converts the co-ordinates to a more workable form
    if len(move) == 4:
        x = move[0:2]
        y = move[2:5]
        move = [x, y]
        if len(move[0]) == 2 and len(move[1]) == 2:
            try:
                move[0] = list(move[0][::-1])
                move[1] = list(move[1][::-1])
                move[0][0] = int(move[0][0]) - 1
                move[1][0] = int(move[1][0]) - 1
                move[0][1] = int(ord(move[0][1])) - 97
                move[1][1] = int(ord(move[1][1])) - 97
                if move[0][0] >= 0 and move[0][0] <= 7 and move[1][0] >= 0 and move[1][0] <= 7:
                    pass
                else:
                    return False, "Incorrect co-ordinate range inputted"
                if move[0][1] >= 0 and move[0][1] <= 7 and move[1][1] >= 0 and move[1][1] <= 7:
                    pass
                else:
                    return False, "Incorrect co-ordinate range inputted"
                return True, move

            except:
                return False, "Incorrect co-ordinates, the orientation should be the x and y co-ordinate written as \"xy\" not \"yx\""
        else:
            return False, "Incorrect co-ordinates, a co-ordinate requires atleast the x and y co-ordinate"

    else:
        return False, "Incorrect Syntax"

def player_colour(uname, session_store):
    if session_store["white"] == uname:
        return "w"
    elif session_store["black"] == uname:
        return "b"
    else:
        return False

def possible_valid_move(colour, move, board, turn):
    # checks if the move doesn't cause the player to take his own piece
    if colour == "w":
        if turn:
            pass
        else:
            return False, "It is not your turn"
    else:
        if not(turn):
            pass
        else:
            return False, "It is not your turn"
    
    if board[move[0][0]][move[0][1]] == "":
        return False, "You cannot move an empty spot"

    elif colour == board[move[0][0]][move[0][1]][0]:
        if board[move[1][0]][move[1][1]] == "":
            return True, "DummyVar"

        elif colour != board[move[1][0]][move[1][1]][0]:
            return True, "DummyVar"

        else:
            return False, "Select a correct spot to move onto that's not possessed by you"

    else:
        return False, "Select a correct piece to move"

def pawn(move, board):
    y_1 = move[0][0]
    x_1 = move[0][1]
    y_2 = move[1][0]
    x_2 = move[1][1]
    path = []
    if board[y_1][x_1][0] == "w":
        if y_1 == 1:
            for i in range(2):
                if board[y_1 + i + 1][x_1]:
                    break
                else:
                    path += [[y_1 + i + 1, x_1]]

        else:
            if not(board[y_1 + 1][x_1]):
                path += [[y_1 + 1, x_1]]

        if x_1 - 1 >= 0:
            if board[y_1 + 1][x_1 - 1]:
                path += [[y_1 + 1, x_1 - 1]]

        if x_1 + 1 <= 7:
            if board[y_1 + 1][x_1 + 1]:
                path += [[y_1 + 1, x_1 + 1]]

    else:
        if y_1 == 6:
            for i in range(2):
                if board[y_1 - i - 1][x_1]:
                    break
                else:
                    path += [[y_1 - i -1, x_1]]

        else:
            if not(board[y_1 - 1][x_1]):
                path += [[y_1 - 1, x_1]]

        if x_1 - 1 >= 0:
            if board[y_1 - 1][x_1 - 1]:
                path += [[y_1 - 1, x_1 - 1]]

        if x_1 + 1 <= 7:
            if board[y_1 - 1][x_1 + 1]:
                path += [[y_1 - 1, x_1 + 1]]
    
    if [y_2, x_2] in path:
        return True
    else:
        return False

def rook(move, board):
    y_1 = move[0][0]
    x_1 = move[0][1]
    y_2 = move[1][0]
    x_2 = move[1][1]
    path = []
    for i in range(y_1):
        if board[y_1 - i - 1][x_1]:
            path += [[y_1 - i - 1, x_1]]
            break
        else:
            path += [[y_1 - i - 1, x_1]]

    for i in range(7 - y_1):
        if board[y_1 + i + 1][x_1]:
            path += [[y_1 + i + 1, x_1]]
            break
        else:
            path += [[y_1 + i + 1, x_1]]
        
    for i in range(x_1):
        if board[y_1][x_1]:
            path += [[y_1, x_1 - i - 1]]
            break
        else:
            path += [[y_1, x_1 - i - 1]]
    
    for i in range(7 - x_1):
        if board[y_1][x_1 + i + 1]:
            path += [[y_1, x_1 + i + 1]]
            break
        else:
            path += [[y_1, x_1 + i + 1]]

    if [y_2, x_2] in path:
        return True
    else:
        return False

def horse(move, board):
    y_1 = move[0][0]
    x_1 = move[0][1]
    y_2 = move[1][0]
    x_2 = move[1][1]
    path = []
    if (y_1 - 2) >= 0 and (x_1 - 1) >= 0:
        path += [[y_1 - 2, x_1 - 1]]

    if (y_1 - 2) >= 0 and (x_1 + 1) <= 7:
        path += [[y_1 - 2, x_1 + 1]]

    if (y_1 + 2) <= 7 and (x_1 - 1) >= 0:
        path += [[y_1 + 2, x_1 - 1]]

    if (y_1 + 2) <= 7 and (x_1 + 1) <= 7:
        path += [[y_1 + 2, x_1 + 1]]

    if (y_1 - 1) >= 0 and (x_1 - 2) >= 0:
        path += [[y_1 - 1, x_1 - 2]]

    if (y_1 - 1) >= 0 and (x_1 + 2) <= 7:
        path += [[y_1 - 1, x_1 - 2]]

    if (y_1 + 1) <= 7 and (x_1 - 2) >= 0:
        path += [[y_1 + 1, x_1 - 2]]

    if (y_1 + 1) <= 7 and (x_1 + 2) <= 7:
        path += [[y_1 + 1, x_1 + 2]]

    if [y_2, x_2] in path:
        return True
    else:
        return False

def bishop(move, board):
    y_1 = move[0][0]
    x_1 = move[0][1]
    y_2 = move[1][0]
    x_2 = move[1][1]
    path = []
    
    q_1 = min(y_1, 7 - x_1)
    q_2 = min(7 - y_1, 7 - x_1)
    q_3 = min(7 - y_1, x_1)
    q_4 = min(y_1, x_1)
    
    for i in range(q_1):
        if board[y_1 - i - 1][x_1 + i + 1]:
            path += [[y_1 - i - 1, x_1 + i + 1]]
            break
        else:
            path += [[y_1 - i - 1, x_1 + i + 1]]

    for i in range(q_2):
        if board[y_1 + i + 1][x_1 + i + 1]:
            path += [[y_1 + i + 1, x_1 + i + 1]]
            break
        else:
            path += [[y_1 + i + 1, x_1 + i + 1]]

    for i in range(q_3):
        if board[y_1 + i + 1][x_1 - i - 1]:
            path += [[y_1 + i + 1, x_1 - i - 1]]
            break
        else:
            path += [[y_1 + i + 1, x_1 - i - 1]]

    for i in range(q_4):
        if board[y_1 - i - 1][x_1 - i - 1]:
            path += [[y_1 - i - 1, x_1 - i - 1]]
            break
        else:
            path += [[y_1 - i - 1, x_1 - i - 1]]

    if [y_2, x_2] in path:
        return True
    else:
        return False

def king(move, board):
    y_1 = move[0][0]
    x_1 = move[0][1]
    y_2 = move[1][0]
    x_2 = move[1][1]
    path = [[y_1 + 1, x_1], [y_1 + 1, x_1 + 1], [y_1, x_1 + 1], [y_1 - 1, x_1 + 1], [y_1 - 1, x_1], [y_1 - 1, x_1 - 1], [y_1, x_1 - 1], [1 + y_1, x_1 - 1]] # hopefully this should be fine due to convert_verify preventing out of range moves

    if [y_2, x_2] in path:
        return True
    else:
        return False

def game_over(board):
    w = False
    b = False
    for i in board:
        if "wk" in i:
            w = True
        
        if "bk" in i:
            b = True

    if not(w):
        return "w"

    elif not(b):
        return "b"

    return False

#### these are here due to global vars instead of funcs

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

######
    
print("Content-Type: text/plain")
print()

try:
    if funcs.check_if_exists(cookie):
        uname = funcs.return_uname(cookie)
        m = funcs.is_ongoing_game(uname)
        if m:
            session_store = open("session_" + str(m[1]), writeback = True)
            board = session_store["board"]
            turn = session_store["turn"]
            move = convert_verify(move)
            if move[0]:
                move = move[1]
                colour = player_colour(uname, session_store)
                possible_valid_move = possible_valid_move(colour, move, board, turn)
                if possible_valid_move[0]:
                    piece = board[move[0][0]][move[0][1]][1]
                    if piece == "p":
                        if pawn(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")

                    elif piece == "r":
                        if rook(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")

                    elif piece == "h":
                        if horse(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")                    
                    elif piece == "b":
                        if bishop(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")

                    elif piece == "q": # queen
                        if rook(move, board) or bishop(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")

                    else:
                        if king(move, board):
                            session_store["turn"] = not(session_store["turn"])
                            board[move[1][0]][move[1][1]] = board[move[0][0]][move[0][1]]
                            board[move[0][0]][move[0][1]] = ""
                            print("Valid move")

                        else:
                            print("Invalid path")

                else:
                    print(possible_valid_move[1])

            else:
                print(move[1])
            
            game = game_over(board)

            if game:
                if game == player_colour(uname, session_store):
                    boolean = False
                else:
                    boolean = True

                fr = handle_forfeit(str(m[1]), uname)
                if fr[0]:
                    update_elo(uname, fr[1], boolean)
                    close_session(str(m[1]), uname, boolean)

        else:
            print("Game over")
            

    session_store.close()
        
except Exception as E:
    print("Error")
    print(E)