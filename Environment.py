import copy

class Environment:
    def __init__(self, board, N, M):
        self.board = copy.deepcopy(board)
        self.rows = N 
        self.columns = M
