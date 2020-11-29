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
        self.basic_heuristic = np.zeros((self.row,self.column))
        self.move_x = [-1, -1, -1 , 0 , 1, 1, 1, 0]
        self.move_y = [-1, 0, 1, 1, 1, 0, -1, -1]
        self.previous_x = -1
        self.previous_y = -1
        self.previous_goal_x = -1
        self.previous_goal_y = -1
        self.generate_heuristic()
        self.transfer_points()
        self.goalx = -1
        self.goaly = -1

    def bonus_each_round(self):
        for i in range(self.row):
            for j in range(self.column):
                if self.map[i][j] == 0:
                    self.heuristic_map[i][j] -= 0.5

    def generate_heuristic(self):
        for i in range(self.row):
            for j in range(self.column):
                if self.map[i][j] == 0:
                    self.calculate_heuristic(i,j)

    def transfer_points(self):
        for i in range(self.row):
            for j in range(self.column):
                self.heuristic_map[i][j] += self.basic_heuristic[i][j]
        #reverse heuristic
        for i in range(self.row):
            for j in range(self.column):
                self.heuristic_map[i][j] *= -1
        self.write_log()

    def write_log(self):
        file = open("thanh.txt","w")
        for i in range(self.row):
            for j in range(self.column):
                file.write(str(int(self.heuristic_map[i][j])) + '  ')
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
                self.basic_heuristic[x][y] += 2**stack
                stack = 0
            if i == 7:
                self.basic_heuristic[x][y] += 2**stack
                stack = 0
            count += 1
            if count == 8:
                count = 0
        
        #diem nhan pham
        self.basic_heuristic[x][y] += random.randint(1,6)

        #spread heuristic
        count = 0
        for i in range(8):
            xx = x + self.move_x[count]
            yy = y + self.move_y[count]
            if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.map[xx][yy] == 0:
                self.heuristic_map[xx][yy] += self.basic_heuristic[x][y]/5
            count += 1

    def make_move(self, x, y, vision_map):

        def get_key(element):
            return element[2]

        #goal must be consistency
        #if goal is not reached, keep goal
        def find_next_goal(curr_x, curr_y):
            sort_array = []
            for i in range(self.row):
                for j in range(self.column):
                    distance = max(abs(curr_x-i),abs(curr_y-j))
                    sort_array.append([i,j,self.heuristic_map[i][j]])
            sort_array.sort(key = get_key)

            min = 9999999 ; ret_x = -1 ; res_y = -1
            if len(sort_array) < self.row:
                max_len = len(sort_array)
            else:
                max_len = self.row
            for i in range(max_len):
                if max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y)) < min:
                    min = max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y))
                    ret_x = sort_array[i][0]
                    ret_y = sort_array[i][1]

            return ret_x,ret_y

        if self.goalx == -1 and self.goaly == -1:
            goal_x, goal_y = find_next_goal(x,y)
            self.goalx = goal_x ; self.goaly = goal_y
        else:
            goal_x = self.goalx ; goal_y = self.goaly
        save_x = 0
        save_y = 0
        min_moves = 9999

        save_x, save_y = self.direct_to_goal(x,y,[goal_x,goal_y])
        if save_x == -1 and save_y == -1:
            if goal_x == 0 and goal_y == 0:
                print("neutralized all spots, terminate!!!")
            else:
                print("could not find a path to goal")
            return 0,0
        
        print(goal_x,goal_y,self.heuristic_map[goal_x,goal_y])

        #for i in range(8):
        #    xx = x + self.move_x[i]
        #    yy = y + self.move_y[i]
        #    if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.map[xx][yy] == 0 and max(abs(xx - goal_x), abs(yy - goal_y))*2 + self.heuristic_map[xx][yy] < min_moves:
        #        min_moves = max(abs(xx - goal_x), abs(yy - goal_y))*2 + self.heuristic_map[xx][yy]
        #        save_x = xx
        #        save_y = yy

        #self.bonus_each_round()
        self.write_log()

        if (save_x == goal_x and save_y == goal_y):
            self.previous_goal_x = save_x
            self.previous_goal_y = save_y
        is_goal = False
        if (x == self.previous_goal_x and y == self.previous_goal_y):
            is_goal = True

        self.previous_x = x
        self.previous_y = y

        self.penalty(is_goal,x,y)
        self.penalty_vision(vision_map,save_x,save_y,goal_x,goal_y)
        return save_x, save_y

    def direct_to_goal(self,init_x,init_y,goal):
        possible_moves = []; parent = []; cost = []

        def mahattan(x,y,goal):
            return max(abs(x - goal[0]), abs(y - goal[1]))
        #unfinished
        def dead_end(x,y):
            if (parent[x][y] == []):
                return False
            full = True
            for i in range(8):
                xx = x + self.move_x[i]
                yy = y + self.move_y[i]
                if (xx < 0 or xx >= self.row or yy < 0 or yy >= self.column or self.map[xx][yy] == 1):
                    continue
                if (parent[xx][yy] != []):
                   full = False
            return full

        for i in range(self.row):
            temp = []; temp2 = []
            for j in range(self.column):
                temp.append([]); temp2.append(999999)
            parent.append(temp)
            cost.append(temp2)

        array = [[init_x,init_y]]; cost[init_x][init_y] = 0
        while (array != [] and not dead_end(goal[0],goal[1])):
            save_x = -1; save_y = -1; save_i = -1; min = 99999

            #find next step to be extended
            for i in range(len(array)):
                xx, yy = array[i]
                if cost[array[i][0]][array[i][1]] + mahattan(xx,yy,goal) + self.heuristic_map[xx][yy]*4 < min:
                    save_x = array[i][0]
                    save_y = array[i][1]
                    min = cost[array[i][0]][array[i][1]] + mahattan(xx,yy,goal) + self.heuristic_map[xx][yy]*4
                    save_i = i
            x = save_x; y = save_y; array.pop(save_i)

            #find all possible moves for current step
            for i in range(8):
                xx = x + self.move_x[i]
                yy = y + self.move_y[i]
                if (xx < 0 or xx >= self.row or yy < 0 or yy >= self.column or self.map[xx][yy] == 1):
                    continue
                if cost[xx][yy] > cost[x][y] + 1:
                    parent[xx][yy] = [x,y]
                    cost[xx][yy] = cost[x][y] + 1
                    array.append([xx,yy])

        if (parent[goal[0]][goal[1]] == []):
              return -1,-1
        trace_x,trace_y = goal
        save_x = -1; save_y = -1
        while True:
            save_x, save_y = parent[trace_x][trace_y]
            if save_x == init_x and save_y == init_y:
                break
            trace_x = save_x; trace_y = save_y
        return trace_x,trace_y


    def global_max(self):
        max = -999999
        save_x = 0
        save_y = 0
        for i in range(self.row):
            for j in range(self.column):
                if self.heuristic_map[i][j] > max and self.map[i][j] == 0:
                    max = self.heuristic_map[i][j]
                    save_x = i
                    save_y = j
        return save_x, save_y

    def global_min(self):
        min = 999999
        save_x = 0
        save_y = 0
        for i in range(self.row):
            for j in range(self.column):
                if self.heuristic_map[i][j] < min and self.map[i][j] == 0:
                    min = self.heuristic_map[i][j]
                    save_x = i
                    save_y = j
        return save_x, save_y

    def penalty(self,is_goal,x,y):
        if self.previous_x == -1 or self.previous_y == -1:
            return
        
        res_x, res_y = self.global_max()
        
        if (is_goal):
            print("reached goal penalty")
            self.heuristic_map[x][y] = self.heuristic_map[res_x][res_y]
            self.goalx = -1; self.goaly = -1
        else:
            penalty_point = abs(self.heuristic_map[x][y] - self.heuristic_map[res_x][res_y]) /10
            self.heuristic_map[x][y] = self.heuristic_map[res_x][res_y]


    def penalty_vision(self,vision_map,x,y,goal_x,goal_y):
        if self.previous_x == -1 or self.previous_y == -1:
            return

        xx, yy = self.global_max()
        penalty_point = abs(self.heuristic_map[xx][yy])/3
        if   (x - self.previous_x == 0):
            sign = y - self.previous_y
            for i in range(self.row):
                for j in range(self.column):
                    if vision_map[i][j] == 1 and self.map[i][j] == 0 and (j-y)*sign > 0:
                        self.heuristic_map[i][j] = self.heuristic_map[xx][yy]
        elif (y - self.previous_y == 0):
            sign = x - self.previous_x
            for i in range(self.row):
                for j in range(self.column):
                    if vision_map[i][j] == 1 and self.map[i][j] == 0 and (i -x)*sign > 0:
                        self.heuristic_map[i][j] = self.heuristic_map[xx][yy]
        else:
            sign_x = x - self.previous_x
            sign_y = y - self.previous_y
            for i in range(self.row):
                for j in range(self.column):
                    if vision_map[i][j] == 1 and self.map[i][j] == 0 and (i -x)*sign_x >= 0 and (j -y)*sign_y >= 0:
                        self.heuristic_map[i][j] = self.heuristic_map[xx][yy]

        #if goal -> pen
        if vision_map[goal_x][goal_y] == 1:
            print("vision goal penalty")
            self.heuristic_map[goal_x][goal_y] = self.heuristic_map[xx][yy]
            self.goalx = -1 ; self.goaly = -1
        
    def breakpoint(self):
        return

            


    
        