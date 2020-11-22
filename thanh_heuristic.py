import copy
import numpy as np

class thanh:
    def __init__(self, map, x, y):
        self.map = copy.deepcopy(map)
        self.row = 0
        self.column = 0
        self.row = len(self.map)
        self.column = len(self.map[0])
        self.heuristic_map = np.zeros((m,n))

    def generate_heuristic(self):
        for i in range(self.row):
            for j in range(self.column):
                if map[i][j] != 1:
                    calculate_heuristic()

    def calculate_heuristic(self, x, y):
        #init
        move_x = [-1, -1, -1 , 0 , 1, 1, 1, 0]
        move_y = [-1, 0, 1, 1, 1, 0, -1, -1]
        start_step = 0
        xx = x + move_x[0]
        yy = y + move_y[0]
        count = 0

        #find start point of the wall
        while self.map[xx][yy] == 1:
            if count == 0:
                count = 7
            else count -= 1
            xx = x + move_x[count]
            yy = y + move_y[count]
        start_step = count

        #calculate h(n)
        stack = 0
        for i in range(8):
            xx = x + move_x[count]
            yy = y + move_y[count]
            if xx < 0 or xx > self.row or yy < 0 or yy > self.column or map[xx][yy] == 1:
                stack += 1
            else:
                self.heuristic_map[x][y] += 2**stack
                stack = 0
            count += 1
            if count == 8:
                count = 0

        #spread heuristic
        count = 0
        for i in range(8):
            xx = x + move_x[count]
            yy = y + move_y[count]
            if xx > 0 and xx < self.row and yy > 0 and yy < self.column:
                self.heuristic_map[xx][yy] += self.heuristic_map[x][y]/2

            


    
        