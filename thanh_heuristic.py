import copy
import numpy as np
import math
import random

class thanh:
    def __init__(self, map):
        self.map = copy.deepcopy(map)
        self.row = 0
        self.column = 0
        self.row = len(self.map)
        self.column = len(self.map[0])
        self.heuristic_map = np.zeros((self.row,self.column))
        self.move_x = [-1, -1, -1 , 0 , 1, 1, 1, 0]
        self.move_y = [-1, 0, 1, 1, 1, 0, -1, -1]
        self.generate_heuristic()


    def generate_heuristic(self):
        for i in range(self.row):
            for j in range(self.column):
                if self.map[i][j] == 0:
                    self.calculate_heuristic(i,j)
        file = open("thanh.txt","w")
        for i in range(self.row):
            for j in range(self.column):
                file.write(str(int(self.heuristic_map[i][j])) + self.spacebar(self.heuristic_map[i][j]))
            file.write('\n')
        file.close()

    def spacebar(self,num):
        if num == 0:
            return '    '
        elif math.log10(int(num)) < 1:
            return '    '
        elif math.log10(int(num)) < 2:
            return '   '
        elif math.log10(int(num)) < 3:
            return '  ' 
        return ' '

    def calculate_heuristic(self, x, y):
        #init
        start_step = 0
        xx = x + self.move_x[0]
        yy = y + self.move_y[0]
        count = 0

        #find start point of the wall
        while True:
            if count == 0:
                count = 7
            else:
                count -= 1
            xx = x + self.move_x[count]
            yy = y + self.move_y[count]
            if xx < 0 or xx >= self.row or yy < 0 or yy >= self.column:
                continue
            if self.map[xx][yy] == 0:
                break
        start_step = count

        #calculate h(n)
        stack = 0
        for i in range(8):
            xx = x + self.move_x[count]
            yy = y + self.move_y[count]
            if xx < 0 or xx >= self.row or yy < 0 or yy >= self.column:
                stack += 1
            elif self.map[xx][yy] == 1:
                stack += 1
            elif self.map[xx][yy] == 0:
                self.heuristic_map[x][y] += 2**stack
                stack = 0
            if i == 7:
                self.heuristic_map[x][y] += 2**stack
                stack = 0
            count += 1
            if count == 8:
                count = 0
        #diem nhan pham
        self.heuristic_map[x][y] += random.randint(1,5)

        #spread heuristic
        count = 0
        for i in range(8):
            xx = x + self.move_x[count]
            yy = y + self.move_y[count]
            if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.map[xx][yy] == 0:
                self.heuristic_map[xx][yy] += self.heuristic_map[x][y]/10
            count += 1

    def make_move(self, x, y):
        self.penalty(x,y)
        max = 0
        xx = 0
        yy = 0
        save_x= 0
        save_y = 0
        for i in range(8):
            xx = x + self.move_x[i]
            yy = y + self.move_y[i]
            if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.heuristic_map[xx][yy] > max:
                max = self.heuristic_map[xx][yy]
                save_x = xx
                save_y = yy
        return save_x, save_y

    def penalty(self,x,y):
        min = 9999
        save_x = 0
        save_y = 0
        for i in range(8):
            xx = x + self.move_x[i]
            yy = y + self.move_y[i]
            if xx > 0 and xx < self.row and yy > 0 and yy < self.column and self.heuristic_map[xx][yy] < min:
                min = self.heuristic_map[xx][yy]
                save_x = xx
                save_y = yy
        self.heuristic_map[x][y] = self.heuristic_map[save_x][save_y] - 2

    
    def breakpoint(self):
        return

            


    
        