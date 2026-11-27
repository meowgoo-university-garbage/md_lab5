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

def game_playMoves(game, moves):
    for move in moves:
        if game is None: return None
        game = game_playMove(game, move)
    return game

def game_isMyTurn(game, value):
    (_, _, players, playerIndex, _) = game
    return players[playerIndex] == value

def game_currentTurn(game):
    (_, _, players, playerIndex, _) = game
    return players[playerIndex]

def game_nextTurn(game):
    (_, _, players, playerIndex, _) = game
    playerIndex += 1
    playerIndex %= len(players)
    return players[playerIndex]

def game_prevTurn(game):
    (_, _, players, playerIndex, _) = game
    playerIndex -= 1
    if playerIndex < 0:
        playerIndex += len(players)
    return players[playerIndex]


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

def game_checkTie(game):
    return len(game_getAllPossibleMoves(game)) == 0

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

def game_isOver(game):
    if len(game_getAllPossibleMoves(game)) == 0: return True
    (_, _, players, _, _) = game
    for p in players:
        if game_checkWin(game, p): return True
    return False

def game_getWinner(game):
    (_, _, players, _, _) = game
    for p in players:
        if game_checkWin(game, p): return p
    if game_checkTie(game): return None
    raise Exception("death")





def mkSearchNode(game, parent = None, move = None, depth = 0):
    (board, winCount, players, playerIndex, moves) = game
    wins = {}
    for p in players:
        wins[p] = 0

    return {
        "game" : game,
        "parent" : parent,
        "move" : move,
        "depth" : depth,
        "wins" : wins,
        "rollouts" : 0,
        "children" : [],
        "work" : [] if game_isOver(game) else game_getAllPossibleMoves(game),
    }

def nodeWinningFraction(node, player):
    return float(node["wins"][player]) / float(node["rollouts"])

def searchMove(game, rounds, temperature, repeats):
    root = mkSearchNode(game)
    
    for round in range(rounds):
        node = root
        while len(node["work"]) == 0 and not game_isOver(node["game"]):
            totalRollouts = sum(child["rollouts"] for child in node["children"])
            best_score = -9999
            best_child = None
            for child in node["children"]:
                exploration = math.sqrt(math.log(totalRollouts) / child["rollouts"])
                winningFraction = 1 - nodeWinningFraction(child, game_currentTurn(child["game"]))
                score = winningFraction + temperature * exploration
                if score > best_score:
                    best_score = score
                    best_child = child

            node = best_child

        if len(node["work"]) > 0 and not game_isOver(node["game"]):
            move = node["work"].pop(random.randrange(len(node["work"])))
            nextGame = game_playMove(node["game"], move)
            newNode = mkSearchNode(nextGame, node, move, node["depth"] + 1)
            node["children"].append(newNode)
            node = newNode

        winners = []
        for _ in range(repeats):
            exploredGame = node["game"]
            while True:
                if game_isOver(exploredGame):
                    winners.append(game_getWinner(exploredGame))
                    break

                move = random.choice(game_getAllPossibleMoves(exploredGame))
                exploredGame = game_playMove(exploredGame, move)

        while node is not None:
            for winner in winners:
                if winner is not None:
                    node["wins"][winner] += 1
                node["rollouts"] += 1
            node = node["parent"]

    def finalScore(node):
        score = 1 - nodeWinningFraction(node, game_nextTurn(game))
        # if score == 0 and nodeWinningFraction(node, game_nextTurn(game)) > 0:
        #     score -= 10
        return score

    # for c in root["children"]:
    #     print(f"{c["wins"]} {c["move"]}")

    best_child = max(root["children"], key = finalScore)
    return best_child["move"]


            



def main():
    if True:
        ts = [ 0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0 ]
        # ts = [ 0.0, 0.25, 0.5 ]
        # ts = [ 2.0 ]
        wins = np.zeros((len(ts), len(ts)))
        for i in range(len(ts)):
            for j in range(len(ts)):
                # if i != j: continue

                t1 = ts[i]
                t2 = ts[j]

                print(f"{t1} vs {t2}")

                result_x = 0
                result_o = 0
                result_tie = 0
                for _ in range(30):
                    game = mkGame(mkBoard(6, 6), 4, [ 'x', 'o' ])
                    while True:
                        if game_isOver(game):
                            if game_checkWin(game, 'x'):
                                result_x += 1
                            if game_checkWin(game, 'o'):
                                result_o += 1
                            if game_checkTie(game):
                                result_tie += 1
                            break

                        # game_printState(game)

                        t = t1 if game_currentTurn(game) == 'x' else t2
                        move = searchMove(game, 200, t, 1)
                        game = game_playMove(game, move)

                wins[i, j] = float(result_x) / float(result_x + result_o + result_tie)
                # wins[i, j] = i / float(len(ts))

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(wins, cmap = "viridis")
        ax.set_ylabel("X")
        ax.set_xlabel("O")
        ax.set_xticks(np.arange(len(ts)))
        ax.set_yticks(np.arange(len(ts)))
        ax.set_xticklabels([f"{t:.1f}" for t in ts])
        ax.set_yticklabels([f"{t:.1f}" for t in ts])
        for i in range(len(ts)):
            for j in range(len(ts)):
                text = ax.text(j, i, f"{wins[i, j]:.1f}%")

        fig.colorbar(im, ax = ax)
        plt.show()

    return

    game = mkGame(mkBoard(3, 3), 3, [ 'x', 'o' ])
    # game = game_playMoves(game, [ (0, 0), (1, 1), (1, 0), (2, 0), (0, 1) ])
    # game = game_playMoves(game, [ (0, 0), (1, 1), (1, 0) ])
    # game = game_playMoves(game, [ (1, 1), (2, 2), (1, 0), (1, 2), (0, 2), (2, 0), (2, 1) ])

    nextGame = None
    while True:
        game_printState(game)

        if game_checkWin(game, 'x'):
            print("X WINS")
            break

        if game_checkWin(game, 'o'):
            print("O WINS")
            break

        if game_checkTie(game):
            print("TIE")
            break

        if game_isMyTurn(game, 'x'):
            v = int(input("Move XY: "))
            x = v // 10
            y = v % 10
            nextGame = game_playMove(game, (x, y))
        else:
            # move = random.choice(game_getAllPossibleMoves(game))
            move = searchMove(game, 1000, 1.2, 1)
            nextGame = game_playMove(game, move)

        if nextGame is None: continue
        game = nextGame



main()
