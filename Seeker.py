import Agent as ag
from heapq import heappush, heappop, heapify
import math
import random
import Obstacle as obs

from queue import Queue
import copy
import numpy as np
import os
from util import util

class Seeker(ag.Agent):
    # def __init__(self, positionx, positiony, sight):
    #     self.soundRange = sight
    #     #mảng 2 chiều đánh dấu số lần thăm các đỉnh tại environment (memory của seeker tại 1 lần chơi)
    #     self.memory = None
    #     super().__init__(positionx, positiony, sight)
    
    def __init__(self, positionx, positiony, sight, soundRange):
        self.soundRange = soundRange
        self.memory = None
        self.memo=None
        self.thanh1=None
        super().__init__(positionx, positiony, sight)
    
    def moveL4(self, environment, announceArray, visionArray, obstacleArray = None, pushableAroundArray = None,level = 1):
        #pass
        #return self.moveL2AStar(environment, announceArray, visionArray)
        #return self.moveL2TSP(environment,announceArray,visionArray)

        return self.moveThanhHeuristic(environment, announceArray, visionArray, obstacleArray, pushableAroundArray,level)
    
    def move(self, environment, announceArray, visionArray, obstacleArray = None, pushableAroundArray = None, level = 1):
        #pass
        env=util.getEvironmentIncludeObs(environment, obstacleArray)
        #return self.moveL2AStar(env, announceArray, visionArray)
        #return self.moveL2TSP(env,announceArray,visionArray)
        return self.moveThanhHeuristic (environment, announceArray, visionArray,obstacleArray,pushableAroundArray, level)

    def initVisit(self, environment):
        rows = environment.rows
        columns = environment.columns
        self.memory = [[0 for i in range(rows)] for j in range(columns)]

    def moveL2AStar(self, environment, announceArray, visionArray):
        Inf = float('inf')
        class Node:
            def __init__(self, position, gscore=Inf, fscore=Inf):
                self.position = position
                self.gscore = gscore
                self.fscore = fscore
                self.closed = False
                self.out_heap = True
                self.parent = None
            
            def __lt__(self, b):
                return self.fscore < b.fscore
        
        class NodeDict(dict):

            def __missing__(self, k):
                klist = [k[0], k[1]]
                v = Node(klist)
                self.__setitem__(k, v)
                return v
        
        #cần viết lại hàm này
        def findGoal(position, environment, announceArray, visionArray, memory):
            vc = 1000001
            N = environment.rows
            M = environment.columns

            #nếu hider trong sight thì đánh điểm cao lên
            GoalEval = [[0 for i in range(N)] for j in range(M)]
            for i in visionArray:
                GoalEval[i[0]][i[1]] += vc - heuristicFnc(position, i)

            for i in announceArray:
                GoalEval[i[0]][i[1]] += math.floor(vc / 2) - heuristicFnc(position, i)

            
            maxGoal = GoalEval[0][0]
            goalPosition = [0, 0]
            for i in range(N):
                for j in range(M):
                    if GoalEval[i][j] > maxGoal:
                        maxGoal = GoalEval[i][j]
                        goalPosition = [i, j]
            
            return goalPosition
        
        def reachedGoal(nodePosition, goalPosition):
            return nodePosition == goalPosition

        def heuristicFnc(nodePosition, goalPosition):
            #max(|y-y'|, |x-x'|)
            return max(abs(goalPosition[0] - nodePosition[0]), abs(goalPosition[1] - nodePosition[1]))
        
        def traceBack(currentNode, startNode):
            while (not currentNode.parent is None) and currentNode.parent != startNode:
                currentNode = currentNode.parent
            return currentNode.position
        
        def getNeighbors(current, environment):
            def isInside(ux, uy, rows, columns):
                return (0 <= ux and ux < rows and 0 <= uy and uy < columns)
            result = []

            x = current[0]
            y = current[1]
            # dx = [-1, -1, -1, 0, 0, 1, 1, 1]
            # dy = [-1, 0, 1, -1, 1, -1, 0, 1]

            #tạo sự ngẫu nhiên của thuật toán về hướng di chuyển
            dxy = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]

            random.shuffle(dxy)
            for i in range(8):
                # ux = x + dx[i]
                # uy = y + dy[i]
                ux = x + dxy[i][0]
                uy = y + dxy[i][1]
                
                if isInside(ux, uy, environment.rows, environment.columns) and environment.board[ux][uy] != 1:
                    result.append((ux, uy))
            return result
        #? neu khong tim duoc goal hop ly???

        #init for A-star
        #nếu là turn đầu
        if self.memory is None:
            self.initVisit(environment)

        goalPosition = findGoal(self.position, environment, announceArray, visionArray, self.memory)
        #print('goal: ', goalPosition)
        startNode = Node(self.position, gscore=0, fscore=heuristicFnc(self.position,goalPosition))

        #tạo map từ position đến Node
        nodeDict = NodeDict()
        nodeDict[(self.position[0], self.position[1])] = startNode
        
        #khởi tạo heap
        openSet = []
        heappush(openSet, startNode)
        while openSet:
            #lấy node lớn nhất
            current = heappop(openSet)
            #đã tới goal
            #self.memory[current.position[0]][current.position[1]] += 1
            if reachedGoal(current.position, goalPosition):
                return traceBack(current, startNode)
            #đưa ra khỏi heap
            current.out_heap = True
            #đưa vào explored set
            current.closed = True
            #print('current pos: ', current.position)
            for u in map(lambda n: nodeDict[n], getNeighbors(current.position, environment)):
                # if current.position == [2, 2]:
                #     print(u.position)
                #print('uGscore: ', u.gscore)
                if u.closed:
                    continue
                uGscore = current.gscore + 1 #khoang cach tu node hien tai den cac dinh ke la 1
                #print('uGscore: ', u.position, uGscore)
                if uGscore >= u.gscore:
                    continue
                u.parent = current
                u.gscore = uGscore
                u.fscore = uGscore + heuristicFnc(u.position, goalPosition)
                if u.out_heap:
                    u.out_heap = False
                    heappush(openSet, u)
                    #print('push heap', u.position)
                else:
                    openSet.remove(u)
                    heappush(openSet, u)
        return None
    
    def getVision(self, environment, obstacleArray):
        #return mang 2d {0,1} 
        #0 la ko co sight
        #1 la co sight
        #Use self.sight 
        environment=util.getEvironmentIncludeObs(environment, obstacleArray)
        nrow=environment.rows
        ncol=environment.columns
        a=[[0 for j in range(ncol)] for i in range (nrow)]

        def setCell (cell,val):
            if (cell[0]<nrow and cell[0]>=0 and cell[1]>=0 and cell[1]<ncol):
                a[cell[0]][cell[1]]=val

        # By default, we allow agent to see all cell within his sight
        for r in range(self.position[0]-self.sight, self.position[0]+self.sight+1, 1):
            for c in range(self.position[1]-self.sight, self.position[1]+self.sight+1, 1):
                setCell([r,c], 1)
        
        # Return coordinate of 16 generated cell (first cell is orig)
        # See image in pdf
        # rfactor and cfactor for generating symmetry. By default, it generates same as pdf
        # rfactor and cfactor should be 1 or -1
        def genCell (orig, rfactor=1, cfactor=1):
            r,c=orig
            dr=[0,-1,-1,0,-2,-2,-2,-1,0,-3,-3,-3,-3,-2,-1,0]
            dc=[0,0,1,1,0,1,2,2,2,0,1,2,3,3,3,3]
            cells=[]
            for i in range(len(dr)):
                cells.append([r+dr[i]*rfactor, c+dc[i]*cfactor])
            return cells

        def obstacle (c):
            if (c[0]<0 or c[0]>=nrow or c[1]<0 or c[1]>=ncol):
                return False
            return environment.board[c[0]][c[1]]==1     #default rule, can be changed
        
        # Implementation the rule stated in pdf
        # c is the list of 16 position stated as in pdf
        def considerVision (c):
            
            # ? If a cell is wall, its vision is 0 or 1
            # This version set vision of a next-to-agent-wall to 1 (we can see it anyway, since its a wall)
            # i.e walls cover another cells but don't cover themselves

            if obstacle(c[1]):
                setCell(c[4],0); setCell(c[9],0)
            if obstacle(c[4]):
                setCell(c[9],0)
            if obstacle(c[3]):
                setCell(c[8],0); setCell(c[15],0)
            if obstacle(c[8]):
                setCell(c[15],0)
            if obstacle(c[2]):
                setCell(c[6],0); setCell(c[12],0)
            if obstacle(c[6]):
                setCell(c[12],0)
                
            if obstacle(c[5]):
                setCell(c[10],0); setCell(c[11],0)
            if obstacle(c[7]):
                setCell(c[13],0); setCell(c[14],0)
            
            # What does "hide more" mean? I would hide it anyway
            if obstacle(c[2]):
                setCell(c[11],0); setCell(c[13],0)
            if obstacle(c[1]):
                setCell(c[10],0)
            if obstacle(c[3]):
                setCell(c[14],0)

            # New rule, appended
            if obstacle(c[1]) and obstacle(c[2]):
                setCell(c[5],0)
            if obstacle(c[2]) and obstacle(c[3]):
                setCell(c[7],0)

        c = genCell(self.position, 1, 1)
        considerVision(c)
        c = genCell(self.position, 1, -1)
        considerVision(c)
        c = genCell(self.position, -1, 1)
        considerVision(c)
        c = genCell(self.position, -1, -1)
        considerVision(c)

        return a
    
    def moveL2TSP (self, environment, announceArray, visionArray):

        '''
        x DFS / BFS to know what cell is "reachable" (we don't bother visiting unreachable cells)
        (Due to laziness / time constraint, I assume all not-wall cells are reachable)
        [c] Build MST using reachable cell (Observe that in this case, finding MST is the same as BFS tree)
            (After some experiment, we observe that DFS tree is more "natural")
        [r] Find an Eulerian tour on MST
        [] Find TSP (not necessarily return to inital cell) using 2-approximation TSP algorithm
        [] Cache the tour somewhere
        '''

        class Memo: # Memorize
            def __init__ (self, nr, nc):
                self.nr=nr; self.nc=nc  # numrow, numcol
                self.visit=[[0 for j in range(nc)] for i in range(nr)]
                self.trace=[[[0,0] for j in range(nc)] for i in range(nr)]

                # Mang 4 chieu d[r][c][k] (k la huong)
                self.ndir=8
                self.d=[[[0 for k in range(self.ndir)] for j in range(nc)] for i in range(nr)]
                self.dr=[-1,-1,0,1,1,1,0,-1]; self.dc=[0,-1,-1,-1,0,1,1,1]

            def reset(self):
                for i in range(self.nr):
                    for j in range(self.nc):
                        self.visit[i][j]=0
                        self.trace[i][j]=[0,0]

        firstTurnFlag = False
        if self.memo is None:
            self.memo=Memo(environment.rows, environment.columns)
            firstTurnFlag=True
        memo=self.memo      # if i'm not wrong, memo holds a REFERENCE of self.memo (not a copy)

        def inside (r, c):
            return r>=0 and c>=0 and r<memo.nr and c<memo.nc
        def iswall (r, c):
            return environment.board[r][c] == 1         # Change this
        def reverse_dir (dir):
            return (dir+4)%8
        def trace (start, cur):                      # Return list 
            ans=[]
            while cur != start:
                ans.append(cur)
                cur=memo.trace[cur[0]][cur[1]]
            ans.reverse()
            return ans

        # If goal is not None, return a route to goal
        def BFS (start=self.position, goal=None):    #goal=None to create BFS Tree MST
            memo.reset()
            memo.visit[start[0]][start[1]]=1
            q=Queue();q.put(start)
            while not q.empty():
                fr=q.get(); r=fr[0]; c=fr[1]
                if (goal is not None) and fr==goal:
                    return trace(start, goal)
                for i in range(len(memo.dr)):
                    rr=r+memo.dr[i]; cc=c+memo.dc[i]
                    if (inside(rr,cc) and (not iswall(rr,cc)) and memo.visit[rr][cc]==0):
                        memo.visit[rr][cc]=1
                        memo.trace[rr][cc]=[r,c]
                        q.put([rr,cc])

                        # Add 2 edge from (r,c) to (rr,cc)
                        memo.d[r][c][i]+=2
                        memo.d[rr][cc][reverse_dir(i)]+=2

        def Eulerian():
            memo.euler=[]
            def findtour (r,c):
                for i in range(memo.ndir):
                    rr=r+memo.dr[i]; cc=c+memo.dc[i]
                    if (memo.d[r][c][i]>0):
                        memo.d[r][c][i] -= 1
                        memo.d[rr][cc][reverse_dir(i)] -= 1
                        findtour(rr,cc)
                memo.euler.append([r,c])
            findtour (self.position[0], self.position[1])

        def DFS ():
            def visit(r,c):
                memo.visit[r][c]=1
                for i in range(memo.ndir):
                    rr=r+memo.dr[i]; cc=c+memo.dc[i]
                    if inside(rr,cc) and (not iswall(rr,cc)) and memo.visit[rr][cc]==0:
                        memo.trace[rr][cc]=[r,c]
                        # Add 2 edge from (r,c) to (rr,cc)
                        memo.d[r][c][i]+=2
                        memo.d[rr][cc][reverse_dir(i)]+=2
                        visit(rr,cc)
            visit(self.position[0], self.position[1])

        # Because of laziness, I do not optimize the Eulerian path here
        # I just go along the Eulerian_path
        def TSP():
            memo.route=memo.euler.copy()
            memo.route.reverse()      # Reverse it to pop faster, since first element is now last.
            memo.route.pop()          # First element (the initial one) is not considered

        # Improve from TSP(): now prune the path down by using A*
        def TSP_v2():
            for i in range(memo.nr):
                for j in range(memo.nc):
                    memo.visit[i][j]=0
            memo.tsp=[]
            # Remove duplicates
            for pos in memo.euler:
                if memo.visit[pos[0]][pos[1]]==0:
                    memo.tsp.append(pos)
                    memo.visit[pos[0]][pos[1]]=1
            memo.route=[]
            st=memo.tsp[0]
            for i in range(1,len(memo.tsp)):
                pos=memo.tsp[i]
                tmp=BFS(st, pos)
                memo.route.extend(tmp)
                st=pos
            memo.route.reverse()    # Reverse it to pop faster, since first element is now last.

        # I'm not responsible for reversing the memo.route
        def go():   # Remember to reverse memo.route BEFORE calling go()
            if memo.route:
                # print("memo.tsp len = "+str(len(memo.tsp)))
                nextloc=memo.route.pop()
                return nextloc
            else:
                # Stay still (we went all the way --> some hiders are unreachable)
                return None


        if firstTurnFlag == True:
            # Using BFS Tree as MST
            #BFS()
            # Using DFS Tree as MST
            DFS()
            Eulerian()
            TSP_v2()
        return go()

    def moveThanhHeuristic (self, environment, announceArray, visionArray, obs_list,pushable_list,level):
        if self.thanh1 is None:
            #self.thanh1 = thanh_heuristic.thanh(environment.board)
            self.thanh1 = thanh(environment.board)

        # Cần sửa signature của thanh.make_move lại, visionArray nhận các vị trí hider nhìn thấy
        # Xem dòng 76 của Engine.py
        newpos = self.thanh1.make_move(self.position[0], self.position[1], self.getVision(environment, obs_list), announceArray, visionArray,obs_list,pushable_list)
        # Because newpos is tuple (... :< pair programming không để ý)
        if level <= 3:
            return [newpos[1],newpos[2]]
        else:
            return newpos[0],[newpos[1],newpos[2]]





#---------------------------thanh_heuristic-------------------------------------------------
class thanh:
    def __init__(self, map):
        self.row = len(map)
        self.column = len(map[0])
        #wall + obs every turn
        self.map = copy.deepcopy(map)
        #original wall
        self.map_copy = copy.deepcopy(map)
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
        #cannot change this copy
        self.heuristic_map_copy = copy.deepcopy(self.heuristic_map)
        #feel free to change this copy
        self.heuristic_map_copy_temp = copy.deepcopy(self.heuristic_map)
        self.reachable_map = None
        self.rear_obstacles_map = np.zeros((self.row,self.column))

    def check_pushable_obs(self, obs,pushable_obs_list):
        if pushable_obs_list is None or pushable_obs_list == []:
            return True
        for i in range(len(pushable_obs_list)):
            if obs.upperLeft == pushable_obs_list[i].upperLeft:
                return False
        return True

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
        already_zero = True
        #find start point of the wall
        while True:
            if count == 0:
                if already_zero:
                    count = 7
                    already_zero = False
                else:
                    break
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
        #self.request_print("chase mode: ON")
        random.shuffle(hider_loc)
        sort_array = []
        def get_key(element):
            return element[2]
        for i in range(len(hider_loc)):
            sort_array.append([hider_loc[i][0],hider_loc[i][1], max(abs(hider_loc[i][0]-x),abs(hider_loc[i][1]-y))])
        #find the closet hider
        sort_array.sort(key = get_key)

        self.goalx = sort_array[0][0] ; self.goaly = sort_array[0][1]
        goal_x = self.goalx ; goal_y = self.goaly

        self.request_print("chase: found hider at: " + str(self.goalx) + ' ' + str(self.goaly))
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
        #self.penalty_vision(vision_map,ret_x,ret_y,goal_x,goal_y)

        return ret_x, ret_y

    def request_print(self, str):
        if (str != self.print_to_console):
            self.print_to_console = str
            print(self.print_to_console)

    def explore_mode(self, x,y, vision_map, obs_list, pushable_obs_list):
        def get_key(element):
            return element[2]

        #goal must be consistency
        #if goal is not reached, keep goal
        def find_next_goal(curr_x, curr_y):
            sort_array = []
            for i in range(self.row):
                for j in range(self.column):
                    if i != x and y != j and self.reachable_map[i][j] == 1:
                        sort_array.append([i,j,self.heuristic_map[i][j]])
            sort_array.sort(key = get_key)

            #find next goal, in top n (n = total row of board), take the closest goal to be goal
            min = 9999999 ; ret_x = -1 ; ret_y = -1
            max_x, max_y = self.global_max()
            min_x, min_y = self.global_min()
            if len(sort_array) < self.row:
                max_len = len(sort_array)
            else:
                max_len = self.row
            for i in range(max_len):
                #not least potential goal and closest
                if self.heuristic_map[max_x][max_y] != sort_array[i][2] and max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y)) < min and sort_array[i][2]*1.1 >= self.heuristic_map[min_x][min_y]:
                    min = max(abs(sort_array[i][0]-curr_x),abs(sort_array[i][1]-curr_y))
                    ret_x = sort_array[i][0]
                    ret_y = sort_array[i][1]

            return ret_x,ret_y

        #if goal is not set -> find a new goal
        if self.goalx == -1 and self.goaly == -1:
            goal_x, goal_y = find_next_goal(x,y)
            self.goalx = goal_x ; self.goaly = goal_y
        else:
            #if goal is current step -> find a new goal
            if self.goalx == x and self.goaly == y:
                goal_x, goal_y = find_next_goal(x,y)
            else:
                goal_x = self.goalx ; goal_y = self.goaly


        def get_key_sim(element):
            return element[3]
        #try pushing around
        simulation_array = self.try_pushing(x,y, pushable_obs_list)
        simulation_array.sort(key = get_key_sim)
        if simulation_array != []:
            best_x,best_y = self.accessible_global_min(x,y)
            #push results > best we temporary got -> decide to push
            if simulation_array[0][3] < self.heuristic_map[best_x][best_y]:
                save_x = simulation_array[0][0] ; save_y = simulation_array[0][1]
                obs_code = simulation_array[0][4] ; direction = simulation_array[0][5]

                #suppose that we already pushed the obstacle -> replace current goal to be the next goal
                print("best goal: ", str(best_x), str(best_y), self.heuristic_map[best_x][best_y], "potential goal: ", simulation_array[0][2], simulation_array[0][3])
                #os.system("pause")
                self.goalx = simulation_array[0][2][0] ; self.goaly = simulation_array[0][2][1]

                #find THE obstacle to push
                for i in range(len(obs_list)):
                    if obs_list[i].upperLeft == pushable_obs_list[obs_code].upperLeft:
                        obs_list[i].move(direction)
                        break
                return obs_list, save_x, save_y

        save_x = -1 ; save_y = -1
        save_x, save_y = self.direct_to_goal(x,y,[goal_x,goal_y])
        if save_x == -1 or save_y == -1 or goal_x == -1 or goal_y == -1:
            #self.breakpoint()
            #goal is not valid
            if goal_x == -1 or goal_y == -1:
                self.request_print("neutralize all spots, terminate!!!")
                self.restart_heuristic_map()
                self.request_print("TRIGGER: heuristic map restart")
            #step is not valid
            elif save_x == -1 or save_y == -1:
                self.request_print("WARNING: could not find a path to goal: " + str(goal_x) + ' ' + str(goal_y))
                min_x,min_y = self.global_max()
                self.heuristic_map[goal_x][goal_y] = self.heuristic_map[min_x][min_y]
                self.request_print("WARNING: neutralized goal at: " + str(goal_x) + ' ' + str(goal_y) + " with " + str(self.heuristic_map[goal_x][goal_y]))
                self.goalx = -1 ; self.goaly = -1
            return obs_list, -1, -1
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
        return obs_list, save_x, save_y

    def restart_heuristic_map(self):
        self.heuristic_map = copy.deepcopy(self.heuristic_map_copy)

    def bonus_announce(self,announce_loc,x,y):
        minx,miny = self.accessible_global_min(x,y)
        self.request_print("announce bonus at " + str(announce_loc[0]))
        for k in range(len(announce_loc)):
            curr_x = announce_loc[k][0] ; curr_y = announce_loc[k][1]
            for i in range(-3,4,1):
                for j in range(-3,4,1):
                    xx = curr_x + i
                    yy = curr_y + j
                    if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.map[x][y] == 0:
                        self.heuristic_map[xx][yy] -= 5

    #trigger after map is updated with obs
    def discover_by_bfs(self, x,y):
        self.reachable_map = np.zeros((self.row,self.column))
        self.reachable_map[x][y] = 1
        array = [[x,y]]
        while (array != []):
            #find all cells to be extended
            curr_x = array[0][0] ; curr_y = array[0][1]
            for i in range(8):
                xx = self.move_x[i] + curr_x
                yy = self.move_y[i] + curr_y
                if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.reachable_map[xx][yy] == 0 and self.map[xx][yy] == 0:
                    array.append([xx,yy])
                    self.reachable_map[xx][yy] = 1
            array.pop(0)
        #print(self.reachable_map)
        #os.system("pause")

    def make_obs_wall(self,obs_list,pushable_obs_list):
        self.map = copy.deepcopy(self.map_copy)
        self.heuristic_map_copy_temp = copy.deepcopy(self.heuristic_map)
        for i in range(len(obs_list)):
            #if self.check_pushable_obs(obs_list[i],pushable_obs_list):
                row = obs_list[i].size[0]
                col = obs_list[i].size[1]
                for j in range(obs_list[i].upperLeft[0], obs_list[i].upperLeft[0]+row):
                    for k in range(obs_list[i].upperLeft[1], obs_list[i].upperLeft[1]+col):
                        self.map[j][k] = 1
                        self.heuristic_map[j][k] = 0 

    def try_pushing(self, x,y, pushable_obs_list):
        if pushable_obs_list == None or pushable_obs_list == []:
            return []
        #simulate possible obs around seeker
        self.heuristic_map_copy_temp = copy.deepcopy(self.heuristic_map)
        simulate_obs_map = np.zeros((self.row, self.column))
        for i in range(len(pushable_obs_list)):
            row = pushable_obs_list[i].size[0]
            col = pushable_obs_list[i].size[1]
            for j in range(pushable_obs_list[i].upperLeft[0], pushable_obs_list[i].upperLeft[0]+row):
                for k in range(pushable_obs_list[i].upperLeft[1], pushable_obs_list[i].upperLeft[1]+col):
                    simulate_obs_map[j][k] = i+1
        save_res_array = []
        #check neighbor step
        for i in range(8):
            next_x = x + self.move_x[i]
            next_y = y + self.move_y[i]
            #check violate obs, if simulate_map is not zero -> occupied
            if next_x >= 0 and next_x < self.row and next_y >= 0 and next_y < self.column and simulate_obs_map[next_x][next_y] != 0:
                obs_code = int(simulate_obs_map[next_x][next_y] - 1)
                row = pushable_obs_list[obs_code].size[0]
                col = pushable_obs_list[obs_code].size[1]
                #check the right direction to push
                if next_x - x > 0 and pushable_obs_list[obs_code].down:
                    #start simulation: move obs to new position: take out -> put back in at new position
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("down")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0
                    
                    #find best value seeker can seek after the simulation
                    best_res = self.accessible_global_min(next_x,next_y)
                    save_res_array.append([next_x,next_y,best_res,self.heuristic_map[best_res[0],best_res[1]],obs_code,"down"])

                    #reset to origial map, exit simulation
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("up")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0

                elif next_x - x < 0 and pushable_obs_list[obs_code].up:
                    #start simulation: move obs to new position: take out -> put back in at new position
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("up")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0
                    
                    #find best value seeker can seek after the simulation
                    best_res = self.accessible_global_min(next_x,next_y)
                    save_res_array.append([next_x,next_y,best_res,self.heuristic_map[best_res[0],best_res[1]],obs_code,"up"])

                    #reset to origial map, exit simulation
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("down")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0

                if next_y - y > 0 and pushable_obs_list[obs_code].right:
                    #start simulation: move obs to new position: take out -> put back in at new position
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("right")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0
                    
                    #find best value seeker can seek after the simulation
                    best_res = self.accessible_global_min(next_x,next_y)
                    save_res_array.append([next_x,next_y,best_res,self.heuristic_map[best_res[0],best_res[1]],obs_code,"right"])

                    #reset to origial map, exit simulation
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("left")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0

                elif next_y - y < 0 and pushable_obs_list[obs_code].left:
                    #start simulation: move obs to new position: take out -> put back in at new position
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("left")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0
                    
                    #find best value seeker can seek after the simulation
                    best_res = self.accessible_global_min(next_x,next_y)
                    save_res_array.append([next_x,next_y,best_res,self.heuristic_map[best_res[0],best_res[1]],obs_code,"left"])

                    #reset to origial map, exit simulation
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 0
                            self.heuristic_map[j][k] = self.heuristic_map_copy_temp[j][k]
                    pushable_obs_list[obs_code].move("right")
                    for j in range(pushable_obs_list[obs_code].upperLeft[0], pushable_obs_list[obs_code].upperLeft[0]+row):
                        for k in range(pushable_obs_list[obs_code].upperLeft[1], pushable_obs_list[obs_code].upperLeft[1]+col):
                            self.map[j][k] = 1
                            self.heuristic_map[j][k] = 0

        return save_res_array
                    
    def bonus_rear_obstacles(self, obs_list):
        self.rear_obstacles_map = np.zeros((self.row,self.column))
        for i in range(len(obs_list)):
            row = obs_list[i].size[0]
            col = obs_list[i].size[1]
            for j in range(obs_list[i].upperLeft[0], obs_list[i].upperLeft[0]+row):
                for k in range(obs_list[i].upperLeft[1], obs_list[i].upperLeft[1]+col):
                    for l in range(8):
                        xx = j + self.move_x[l]
                        yy = k + self.move_y[l]
                        if xx >= 0 and xx < self.row and yy >= 0 and yy < self.column and self.map[xx][yy] == 0 and not obs_list[i].is_moved_once():
                            self.rear_obstacles_map[xx][yy] = 1

    def make_move(self, x, y, vision_map, announce_loc, hider_loc,obs_list1, pushable_obs_list1):
        obs_list = copy.deepcopy(obs_list1)
        pushable_obs_list = copy.deepcopy(pushable_obs_list1)

        #make obs all wall if obs can't be pushed
        self.make_obs_wall(obs_list,pushable_obs_list)
        if obs_list != [] and obs_list != None:
            self.bonus_rear_obstacles(obs_list)

        self.discover_by_bfs(x,y)

        #hider is spotted
        if hider_loc != []:
            save_x,save_y = self.chase_mode(x,y,vision_map ,hider_loc)
        else:
            if announce_loc != []:
                self.bonus_announce(announce_loc,x,y)

            obs_list, save_x, save_y = self.explore_mode(x,y,vision_map,obs_list, pushable_obs_list)

        if save_x == -1 and save_y == -1:
            while save_x < 0 or save_y < 0 or save_x >= self.row or save_y >= self.column or self.map[save_x][save_y]==1:
                count = random.randint(0,7)
                save_x = x + self.move_x[count] ; save_y = y + self.move_y[count]
            self.request_print("WARNING: random step taken at: " + str(save_x) + ' ' + str(save_y))

        self.heuristic_map_copy_temp = copy.deepcopy(self.heuristic_map)
        return obs_list, save_x, save_y

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

    def accessible_global_max(self,x,y):
        self.discover_by_bfs(x,y)
        max = -999999; ret_x = -1; ret_y = -1
        for i in range(self.row):
            for j in range(self.column):
                if self.heuristic_map[i][j] > max and self.reachable_map[i][j] == 1:
                    max = self.heuristic_map[i][j]
                    ret_x = i
                    ret_y = j
        return ret_x,ret_y

    def accessible_global_min(self,x,y):
        self.discover_by_bfs(x,y)
        min = 999999; ret_x = -1; ret_y = -1
        for i in range(self.row):
            for j in range(self.column):
                if self.heuristic_map[i][j] < min and self.reachable_map[i][j] == 1:
                    min = self.heuristic_map[i][j]
                    ret_x = i
                    ret_y = j
        return ret_x,ret_y

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
            self.previous_goal_x = -1; self.previous_goal_y = -1
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
                if vision_map[i][j] == 1 and self.map[i][j] == 0 and self.rear_obstacles_map[i][j] != 1:
                    self.heuristic_map[i][j] = self.heuristic_map[xx][yy]

        #if goal -> pen
        if vision_map[goal_x][goal_y] == 1:
            self.heuristic_map[goal_x][goal_y] = self.heuristic_map[xx][yy]
            self.goalx = -1 ; self.goaly = -1
        
    def breakpoint(self):
        return