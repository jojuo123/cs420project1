import copy
import numpy as np
import math
import random
import os

class thanh:
    def __init__(self, map):
        self.row = len(map)
        self.column = len(map[0])
        self.map = copy.deepcopy(map)
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
        self.print_to_console = ""
        self.heuristic_map_copy = copy.deepcopy(self.heuristic_map)

    def shuffle_neighbor_step(self):
        shuffle_list = []
        for i in range(8):
            shuffle_list.append([self.move_x[i],self.move_y[i]])
        seed = random.randint(1,999999)
        random.seed(seed)
        random.shuffle(shuffle_list)
        for i in range(8):
            self.move_x[i] = shuffle_list[i][0]
            self.move_y[i] = shuffle_list[i][1]

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

    def chase_mode(self, x,y, vision_map, hider_loc):
        self.request_print("chase mode: ON")
        sort_array = []
        def get_key(element):
            return element[2]
        for i in range(len(hider_loc)):
            sort_array.append([hider_loc[i][0],hider_loc[i][1], max(abs(hider_loc[i][0]-x),abs(hider_loc[i][1]-y))])
        #find the closet hider
        sort_array.sort(key = get_key)

        self.goalx = sort_array[0][0] ; self.goaly = sort_array[0][1]
        goal_x = self.goalx ; goal_y = self.goaly

        self.request_print("chase: next goal: " + str(str(goal_x) + ' ' + str(goal_y) + ' ' + str(self.heuristic_map[goal_x,goal_y])))

        ret_x, ret_y = self.direct_to_goal(x,y,[goal_x,goal_y])

        if ret_x == -1 or ret_y == -1 or goal_x == -1 or goal_y == -1:
            self.breakpoint()
            if ret_x == -1 and ret_y == -1:
                self.request_print("chase: neutralize all spots, terminate!!!")
            else:
                self.request_print("chase: could not find a path to goal or already at goal")
            return -1,-1

        #check if this step reaches goal
        if (ret_x == goal_x and ret_y == goal_y):
            self.previous_goal_x = goal_x
            self.previous_goal_y = goal_y
        is_goal = False
        if (x == self.previous_goal_x and y == self.previous_goal_y):
            is_goal = True

        self.previous_x = x ; self.previous_y = y
        self.penalty(is_goal,x,y)
        self.penalty_vision(vision_map,ret_x,ret_y,goal_x,goal_y)

        return ret_x, ret_y

    def request_print(self, str):
        if (str != self.print_to_console):
            self.print_to_console = str
            print(self.print_to_console)

    def explore_mode(self, x,y, vision_map):
        def get_key(element):
            return element[2]

        #goal must be consistency
        #if goal is not reached, keep goal
        def find_next_goal(curr_x, curr_y):
            sort_array = []
            for i in range(self.row):
                for j in range(self.column):
                    sort_array.append([i,j,self.heuristic_map[i][j]])
            sort_array.sort(key = get_key)

            #find next goal, in top n (n = total row of board), take the closest goal to be goal
            min = 9999999 ; ret_x = -1 ; ret_y = -1
            max_x, max_y = self.global_max()
            if len(sort_array) < self.row:
                max_len = len(sort_array)
            else:
                max_len = self.row
            for i in range(max_len):
                if self.heuristic_map[max_x][max_y] != sort_array[i][2] and max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y)) < min:
                    min = max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y))
                    ret_x = sort_array[i][0]
                    ret_y = sort_array[i][1]

            return ret_x,ret_y

        if self.goalx == -1 and self.goaly == -1:
            goal_x, goal_y = find_next_goal(x,y)
            self.goalx = goal_x ; self.goaly = goal_y
        else:
            goal_x = self.goalx ; goal_y = self.goaly

        save_x = -1 ; save_y = -1
        save_x, save_y = self.direct_to_goal(x,y,[goal_x,goal_y])
        if save_x == -1 or save_y == -1 or goal_x == -1 or goal_y == -1:
            self.breakpoint()
            if goal_x == -1 and goal_y == -1:
                self.request_print("neutralize all spots, terminate!!!")
                self.restart_heuristic_map()
                self.request_print("TRIGGER: heuristic map restart")
            else:
                self.request_print("could not find a path to goal or already at goal")
            return -1,-1
        self.request_print("next goal: " + str(goal_x) + ' ' + str(goal_y) + ' ' + str(self.heuristic_map[goal_x,goal_y]))

        #self.bonus_each_round()
        self.write_log()

        #check if this step reaches goal
        if (save_x == goal_x and save_y == goal_y):
            self.previous_goal_x = goal_x
            self.previous_goal_y = goal_y
        is_goal = False
        if (x == self.previous_goal_x and y == self.previous_goal_y):
            is_goal = True

        self.previous_x = x ; self.previous_y = y
        self.penalty(is_goal,x,y)
        self.penalty_vision(vision_map,save_x,save_y,goal_x,goal_y)
        return save_x, save_y

    def restart_heuristic_map(self):
        self.heuristic_map = copy.deepcopy(self.heuristic_map_copy)

    def bonus_announce(self,announce_loc):
        self.request_print("announce bonus at " + str(announce_loc[0]))
        for k in range(len(announce_loc)):
            curr_x = announce_loc[k][0] ; curr_y = announce_loc[k][1]
            for i in range(-3,4,1):
                for j in range(-3,4,1):
                    x = curr_x + i
                    y = curr_y + j
                    if x >= 0 and x < self.row and y >= 0 and y < self.column and self.map[x][y] == 0:
                        self.heuristic_map[x][y] -= self.basic_heuristic[x][y]/10

    def make_move(self, x, y, vision_map, announce_loc, hider_loc):
        if hider_loc != []:
            save_x,save_y = self.chase_mode(x,y,vision_map ,hider_loc)
        else:
            if announce_loc != []:
                self.bonus_announce(announce_loc)
            save_x,save_y = self.explore_mode(x,y,vision_map)
        if save_x == -1 and save_y == -1:
            while save_x < 0 or save_y < 0 or save_x >= self.row or save_y >= self.column or self.map[save_x][save_y]==1:
                count = random.randint(0,7)
                save_x = x + self.move_x[count] ; save_y = y + self.move_y[count]
            self.request_print("random step taken at: " + str(save_x) + ' ' + str(save_y))
        return save_x, save_y

    def direct_to_goal(self,init_x,init_y,goal):
        parent = []; cost = []

        def mahattan(x,y,goal):
            return max(abs(x - goal[0]), abs(y - goal[1]))
        #unfinished
        #def dead_end(x,y):
        #    if (parent[x][y] == []):
        #        return False
        #    full = True
        #    for i in range(8):
        #        xx = x + self.move_x[i]
        #        yy = y + self.move_y[i]
        #        if (xx < 0 or xx >= self.row or yy < 0 or yy >= self.column or self.map[xx][yy] == 1):
        #            continue
        #        if (parent[xx][yy] != []):
        #           full = False
        #    return full
        def dead_end(x,y):
            if (parent[x][y] == []):
                return False
            else:
                return True

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
            self.shuffle_neighbor_step()
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
            self.heuristic_map[x][y] = self.heuristic_map[res_x][res_y]
            self.goalx = -1; self.goaly = -1
        else:
            penalty_point = abs(self.heuristic_map[x][y] - self.heuristic_map[res_x][res_y]) /10
            self.heuristic_map[x][y] = self.heuristic_map[res_x][res_y]


    def penalty_vision(self,vision_map,x,y,goal_x,goal_y):
        if self.previous_x == -1 or self.previous_y == -1:
            return

        xx, yy = self.global_max()
        #penalty_point = abs(self.heuristic_map[xx][yy])/3
        #if   (x - self.previous_x == 0):
        #    sign = y - self.previous_y
        #    for i in range(self.row):
        #        for j in range(self.column):
        #            if vision_map[i][j] == 1 and self.map[i][j] == 0 and (j-y)*sign > 0:
        #                self.heuristic_map[i][j] = self.heuristic_map[xx][yy]
        #elif (y - self.previous_y == 0):
        #    sign = x - self.previous_x
        #    for i in range(self.row):
        #        for j in range(self.column):
        #            if vision_map[i][j] == 1 and self.map[i][j] == 0 and (i -x)*sign > 0:
        #                self.heuristic_map[i][j] = self.heuristic_map[xx][yy]
        #else:
        #    sign_x = x - self.previous_x
        #    sign_y = y - self.previous_y
        #    for i in range(self.row):
        #        for j in range(self.column):
        #            if vision_map[i][j] == 1 and self.map[i][j] == 0 and (i -x)*sign_x >= 0 and (j -y)*sign_y >= 0:
        #                self.heuristic_map[i][j] = self.heuristic_map[xx][yy]

        for i in range(self.row):
            for j in range(self.column):
                if vision_map[i][j] == 1 and self.map[i][j] == 0:
                    self.heuristic_map[i][j] = self.heuristic_map[xx][yy]

        #if goal -> pen
        if vision_map[goal_x][goal_y] == 1:
            self.heuristic_map[goal_x][goal_y] = self.heuristic_map[xx][yy]
            self.goalx = -1 ; self.goaly = -1
        
    def breakpoint(self):
        return