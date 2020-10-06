from random import randint
from itertools import cycle
import unittest

class TicTacGame:
    def __init__(self, pc_player = False, human_first = True, difficulty = 0):
        self.player_pc = pc_player
        self.human_player = { True: "✕", False: "◯"}[human_first]
        self.difficulty = difficulty
        self.board = [[" "] * 3 for _ in range(3)]

    def show_board(self):
        board_str = ((" {} ".format(j) for j in i) for i in self.board)
        board_str = ["│{}│\n".format("│".join(i)) for i in board_str]
        print("╭───┬───┬───╮\n{}╰───┴───┴───╯".format("├───┼───┼───┤\n".join(board_str)))

    def validate_input(self, user_input):
        if user_input == "help" or user_input == "quit" or user_input == "show":
            return True
        elif user_input.split()[0] == "move":
            try:
                _, x, y = user_input.split()
                x = int(x)
                y = int(y)

                if not (0 <= x <= 2 and 0 <= y <= 2):
                    raise ValueError("Wrong user input!")
            except ValueError:
                raise ValueError("Wrong user input!")
            else:
                return True
        
        raise ValueError("Wrong user input!")

    def get_user_input(self):
        while True:
            try:
                user_input = input(" >> ")
                self.validate_input(user_input)
            except ValueError:
                print("Wrong input! Try again")
            else:
                break
        
        if user_input.split()[0] == "move":
            user_input = list(map(int, user_input.split()[1:]))

        return user_input

    def get_pc_move(self):
        if self.difficulty == 0:
            x, y = randint(0, 2), randint(0, 2)

            while self.board[y][x] != " ":
                x, y = randint(0, 2), randint(0, 2)
            
            return (x, y)
        elif self.difficulty == 1:
            if "".join("".join(row) for row in self.board).count(" ") == 9:
                return (1, 1)
            
            _, (x, y) = self.minimax({"◯":"✕", "✕":"◯"}[self.human_player])
            return (x, y)

    def start_game(self):
        for player in cycle("✕◯"):
            if self.player_pc and (player != self.human_player):
                user_input = self.get_pc_move()
            else:
                user_input = self.get_user_input()

                while 1:
                    if user_input == "quit":
                        return
                    elif user_input == "help":
                        print("  Available commands:\n"\
                              "    help     - display this message\n"\
                              "    quit     - end current game session\n"\
                              "    show     - show corrunt playing board\n"\
                              "    move x y - make a move to position x, y on board")
                    elif user_input == "show":
                        self.show_board()
                    else:
                        x, y = user_input[0], user_input[1]
                        if self.board[y][x] == " ":
                            break
                        else:
                            print("Square already taken!")
                    
                    user_input = self.get_user_input()
            
            self.board[user_input[1]][user_input[0]] = player
            self.show_board()

            if self.check_winner():
                winner = self.check_winner()
                if winner == "✕":
                    print("Player 1 won!")
                elif winner == "◯":
                    print("Player 2 won!")
                else:
                    print("It's a tie!")
                
                return

    def translate_player(self, tile):
        if tile == "✕":
            return 1
        elif tile == "◯":
            return -1
        else:
            return 0

    def check_winner(self):
        board = self.board
        sums = [sum(map(self.translate_player, a)) for a in (board[0], board[1], board[2],
                map(lambda a: a[0], board), map(lambda a: a[1], board), map(lambda a: a[2], board),
                map(lambda a: a[1][a[0]], enumerate(board)),
                map(lambda a: a[1][a[0]], enumerate(board[::-1])))]
        for i in sums:
            if i == 3:
                return "✕"
            elif i == -3:
                return "◯"
        
        num_empty = "".join("".join(row) for row in self.board).count(" ")
        if num_empty == 0:
            return "tie"
        
        return 0
    
    def minimax(self, player, depth = 0) :
        if player == "◯": 
            best = -10
        else:
            best = 10

        if self.check_winner() :
            if self.check_winner() == "✕" :
                return -10 + depth, None
            elif self.check_winner() == "tie" :
                return 0, None
            elif self.check_winner() == "◯" :
                return 10 - depth, None
        for y in range(3):
            for x in range(3):
                if self.board[y][x] == " ":
                    self.board[y][x] = player
                    val, _ = self.minimax({"◯":"✕", "✕":"◯"}[player], depth+1)

                    self.board[y][x] = " "
                    if player == "◯" :
                        if val > best :
                            best, bestMove = val, (x, y)
                    else :
                        if val < best :
                            best, bestMove = val, (x, y)

        return best, bestMove

class TicTacTestCase(unittest.TestCase):
    def setUp(self):
        self.game = TicTacGame()
    
    def test_validate_user_input(self):
        with self.assertRaises(ValueError):
            self.game.validate_input("lalala")
        
        self.assertTrue(self.game.validate_input("quit"))
        self.assertTrue(self.game.validate_input("help"))
        self.assertTrue(self.game.validate_input("show"))
        self.assertTrue(self.game.validate_input(f"move {randint(0, 2)} {randint(0, 2)}"))

        with self.assertRaises(ValueError):
            self.game.validate_input(f"move {randint(3, 10)} {randint(3, 10)}")
    
    def test_translate_player(self):
        self.assertEqual(self.game.translate_player("✕"), 1)
        self.assertEqual(self.game.translate_player("◯"), -1)
        self.assertEqual(self.game.translate_player(" "), 0)

    def test_check_winner(self):
        self.game.board[0][0] = "✕"
        self.game.board[1][1] = "✕"
        self.assertEqual(self.game.check_winner(), 0)

        self.game.board[0][2] = "◯"
        self.game.board[2][2] = "✕"
        self.assertEqual(self.game.check_winner(), "✕")

        self.game.board[1][1] = "◯"
        self.game.board[2][0] = "◯"
        self.assertEqual(self.game.check_winner(), "◯")

        self.game.board[2][0] = "✕"
        self.game.board[0][1] = "✕"
        self.game.board[1][2] = "✕"
        self.game.board[2][1] = "◯"
        self.game.board[1][0] = "◯"
        self.assertEqual(self.game.check_winner(), "tie")
    
    def test_get_pc_move(self):
        self.player_pc = True
        self.game.difficulty = 1
        self.game.human_player = "◯"
        self.assertEqual(self.game.get_pc_move(), (1, 1))

        self.game.human_player = "✕"
        self.game.board[1][1] = "✕"
        self.assertEqual(self.game.get_pc_move(), (0, 0))

        self.game.difficulty = 0
        self.game.board[0][0] = "◯"
        self.game.board[0][2] = "✕"
        x, y = self.game.get_pc_move()
        self.assertEqual(self.game.board[y][x], " ")

if __name__ == "__main__":
    game = TicTacGame(pc_player=True, human_first=True, difficulty=1)
    game.start_game()