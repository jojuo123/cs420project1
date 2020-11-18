import copy

class Environment:
    def __init__(self, board):
        self.board = copy.deepcopy(board)
    
    def check_valid_coor(self,x,y):
        max_row = len(self.board)
        max_column = len(self.board[0])
        if x < 0 or x > max_row:
            return False
        if y < 0 or y > max_column:
            return False
        return True

    def visualize_agents(self,seeker,hider):
        if self.check_valid_coor(seeker[0],seeker[1]):
            self.board[seeker[0]][seeker[1]] = 1 #might be corrected later
        else:
            print("invalid coordinate " + str(seeker[0]) + ' ' + str(seeker[1]))
        for i in range(len(hider)):
            if self.check_valid_coor(hider[i][0],hider[i][1]):
                self.board[hider[i][0]][hider[i][1]] = 2 #might be corrected later
            else:
                print("invalid coordinate " + str(hider[i][0]) + ' ' + str(hider[i][1]))
