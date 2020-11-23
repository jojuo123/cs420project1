import Agent as ag
from heapq import heappush, heappop, heapify
import math
import random
from queue import Queue
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
        super().__init__(positionx, positiony, sight)
    
    def move(self, environment, announceArray, visionArray):
        #pass
        #return self.moveL2AStar(environment, announceArray, visionArray)
        return self.moveL2TSP(environment,announceArray,visionArray)

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
    
    def getVision(self, environment):
        #return mang 2d {0,1} 
        #0 la ko co sight
        #1 la co sight
        #Use self.sight 
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
                self.position=nextloc
            else:
                # Stay still (we went all the way --> some hiders are unreachable)
                pass


        if firstTurnFlag == True:
            # Using BFS Tree as MST
            #BFS()
            # Using DFS Tree as MST
            DFS()
            Eulerian()
            TSP_v2()
        go()
        return None