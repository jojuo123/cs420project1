import copy

class Environment:
    def __init__(self, board):
        self.board = copy.deepcopy(board)
