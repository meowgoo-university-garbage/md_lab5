import matplotlib.pyplot as plt
import numpy as np
import math
import time
import random


def mkGame(board, winCount, players, playerIndex = 0, moves = []):
    return (board, winCount, players, playerIndex, moves)

def mkBoard(w, h, cells = []):
    if len(cells) != (w * h):
        cells = [ None for _ in range(w * h) ]
    return (w, h, cells)

def board_modified(board, x, y, value):
    (w, h, cells) = board
    cells = cells.copy()

    if x < 0 or x >= w: return None
    if y < 0 or y >= h: return None
    i = (y * w) + (x * 1)

    if cells[i] is not None: return None
    cells[i] = value

    return mkBoard(w, h, cells)

def board_get(board, x, y):
    (w, h, cells) = board
    if x < 0 or x >= w: return False
    if y < 0 or y >= h: return False
    i = (y * w) + (x * 1)
    return cells[i]

def game_playMove(game, move):
    (board, winCount, players, playerIndex, moves) = game
    (x, y) = move

    board = board_modified(board, x, y, players[playerIndex])
    if board is None: return None

    moves = moves.copy()
    moves.append(move)

    playerIndex += 1
    playerIndex %= len(players)

    return mkGame(board, winCount, players, playerIndex, moves)

def game_isMyTurn(game, value):
    (_, _, players, playerIndex, _) = game
    return players[playerIndex] == value

def game_printState(game):
    (board, winCount, players, playerIndex, moves) = game
    (w, h, cells) = board

    print(f"Player to move: {players[playerIndex]}")
    print("-----")

    for y in range(h):
        print("|", end = "")
        for x in range(w):
            print(board_get(board, x, y) or " ", end = "")
        print("|", end = "\n")
    print("-----")

def game_getAllPossibleMoves(game):
    board = game[0]
    (w, h, cells) = board
    return [ (x, y) for x in range(w) for y in range(h) if board_get(board, x, y) == None ]

def game_checkWin(game, player):
    (board, winCount, players, playerIndex, moves) = game
    (w, h, cells) = board

    for col in range(w):
        consecutive = 0
        for row in range(h):
            if board_get(board, col, row) == player:
                consecutive += 1
            else:
                consecutive = 0

            if consecutive >= winCount: return True

    for row in range(h):
        consecutive = 0
        for col in range(w):
            if board_get(board, col, row) == player:
                consecutive += 1
            else:
                consecutive = 0

            if consecutive >= winCount: return True

    diagonalCount = w + h - 1
    corner_bl = (0, h - 1)
    corner_tl = (0, 0)
    corner_br = (w - 1, h - 1)
    corner_tr = (w - 1, 0)
    step1 = (1, -1)
    step2 = (1, 1)

    pos = corner_bl
    consecutive = 0
    while True:
        (x, y) = pos
        if board_get(board, x, y) == player:
            consecutive += 1
        else:
            consecutive = 0

        if consecutive >= winCount: return True

        if pos == corner_tr: break
        (dx, dy) = step1
        pos = (x + dx, y + dy)

    pos = corner_tl
    consecutive = 0
    while True:
        (x, y) = pos
        if board_get(board, x, y) == player:
            consecutive += 1
        else:
            consecutive = 0

        if consecutive >= winCount: return True

        if pos == corner_br: break
        (dx, dy) = step2
        pos = (x + dx, y + dy)

    return False




def main():
    game = mkGame(mkBoard(3, 3), 3, [ 'x', 'o' ])
    nextGame = None
    while True:
        game_printState(game)

        if game_checkWin(game, 'x'):
            print("X WINS")
            break

        if game_checkWin(game, 'o'):
            print("O WINS")
            break

        if game_isMyTurn(game, 'x'):
            v = int(input("Move XY: "))
            x = v // 10
            y = v % 10
            nextGame = game_playMove(game, (x, y))
        else:
            move = random.choice(game_getAllPossibleMoves(game))
            nextGame = game_playMove(game, move)

        if nextGame is None: continue
        game = nextGame



main()
