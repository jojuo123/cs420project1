import Agent as ag
import random
import Obstacle as obs
import copy
from queue import Queue
from util import util

class Hider(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        self.prob = 0.0
        self.moveGoal_goal = None
        self.tactic_v1 = None
        super().__init__(positionx, positiony, sight)
    
    def Dead(self):
        x = self.position[0]
        y = self.position[1]
        self.position = [-1, -1]
        return x,y
    
    def AnnouncePosition(self, environment, obstacleArray):
        env = util.getEvironmentIncludeObs(environment, obstacleArray)
        array=[]
        for i in range(self.position[0]-3, self.position[0]+4):
            for j in range(self.position[1]-3, self.position[1]+4):
                if i>=0 and i<env.rows and j>=0 and j<env.columns and env.board[i][j]==0:
                    array.append([i,j])
        id=random.randint(0, len(array)-1)
        return array[id]
    
    def Announce(self, environment, obstacleArray):
        if self.prob >= 0.1:
            m = random.random()
            if m < self.prob:
                self.prob = 0
                return self.AnnouncePosition(environment, obstacleArray)
            else:
                self.prob = min(self.prob + 0.1, 1.0)
                return None
        else:
            self.prob = self.prob + 0.1
            return None
    
    def moveProb(self, seekerInSight):
        if (seekerInSight is None):
            return 1.0
        return 1.0

    def initMoveL4(self, environment, seekerInSight, obstacleArray = None, pushableAroundArray = None):
        # Lú
        """
        Nếu xung quanh không có ô nào đẩy được, thì đi như level 3
        Nếu có ô đẩy được (tối đa 4 ô như vậy):
            Thử đẩy rồi tìm map mới
            du:=Số ô unreachable sau đẩy - trước đẩy
            de:=Số ô deadend sau đẩy - trước đẩy
            dm:=Số ô merriable sau đẩy - trước đẩy
            * du càng cao, khả năng đẩy càng thấp
            * de càng cao, khả năng đẩy càng thấp
            * dm càng cao, khả năng đẩy càng cao
            Nhân phẩm sẽ quyết định cuộc chơi
        """
        def getPushDirection(obstacle):
            if obstacle.up:
                return 'up'
            elif obstacle.left:
                return 'left'
            elif obstacle.down:
                return 'right'
            return 'down'
        def getNewPos (position, direction):
            if direction=='up':
                return [position[0]-1, position[1]]
            if direction=='down':
                return [position[0]+1, position[1]]
            if direction=='left':
                return [position[0], position[1]-1]
            if direction=='right':
                return [position[0], position[1]+1]
            return [position[0], position[1]]

        old_env=util.getEvironmentIncludeObs(environment, obstacleArray)
        old_ttc=TacticV1(old_env, obstacleArray)
        old_ttc.generateMapReachable(self.position, old_env, obstacleArray)

        if pushableAroundArray is None or pushableAroundArray == []:
            # Vì đây là moveInit nên không bị ảnh hưởng bởi moveProb
            return obstacleArray, old_ttc.move(self, old_env, seekerInSight, obstacleArray)
        else:
            candidate_ids = []
            for id in range(0,len(pushableAroundArray)):
                pushablArr=copy.deepcopy(pushableAroundArray)
                obsArr=copy.deepcopy(obstacleArray)
                direction=getPushDirection(pushablArr[id])

                obsArr.remove(pushablArr[id])
                pushablArr[id].move(direction)
                obsArr.append(pushablArr[id])

                new_env=util.getEvironmentIncludeObs(environment, obsArr)
                new_pos=getNewPos (self.position, direction)
                ttc=TacticV1(new_env, obstacleArray)
                ttc.generateMapReachable(new_pos,new_env,obstacleArray)

                """
                du:=Số ô unreachable sau đẩy - trước đẩy
                de:=Số ô deadend sau đẩy - trước đẩy
                dm:=Số ô merriable sau đẩy - trước đẩy
                * du càng cao, khả năng đẩy càng thấp
                * de càng cao, khả năng đẩy càng thấp
                * dm càng cao, khả năng đẩy càng cao
                """
                du=ttc.numUnreachableCell() - old_ttc.numUnreachableCell()
                de=ttc.numDeadendCell()-old_ttc.numDeadendCell()
                dm=ttc.numMerriableCell()-old_ttc.numMerriableCell()

                if dm>0 or de<0:
                    candidate_ids.append(id)
                # Tính cách của tác giả dòng code này: 60% lý trí
                # 40% chơi ngu
                if (random.random()<0.4):   
                    candidate_ids.append(id)

            if (candidate_ids == []):
                return obstacleArray, old_ttc.move(self, old_env, seekerInSight, obstacleArray)

            # Triệu hồi Rồng Nhân Phẩm rồi đẩy
            id = random.randint(0,len(candidate_ids)-1)
            pushablArr=copy.deepcopy(pushableAroundArray)
            obsArr=copy.deepcopy(obstacleArray)
            direction=getPushDirection(pushablArr[id])

            obsArr.remove(pushablArr[id])
            pushablArr[id].move(direction)
            obsArr.append(pushablArr[id])

            new_pos=getNewPos (self.position, direction)
            return obsArr, new_pos
        # return None, None #obs list mới, vị trí mới
    
    def move(self, environment, seekerInSight, obstacleArray = None):
        p = self.moveProb(seekerInSight)

        def canMove (prob):
            rnd=random.random()
            return rnd<prob
        if not canMove(prob=p):     # Hider won't move this turn
            return None

        env = util.getEvironmentIncludeObs(environment, obstacleArray)
        #return self.moveRandomDirection (env, seekerInSight) # Now move random
        #return self.moveGoalAStar (env, seekerInSight, goal=None) #Random goal
        return self.moveTacticV1 (env, seekerInSight, obstacleArray)

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
        
    def moveRandomDirection(self, environment, seekerInSight):
        def inside (r, c):
            nr, nc=[environment.rows, environment.columns]
            return r>=0 and r<nr and c>=0 and c<nc
        dr=[-1,0,1,1,1,0,-1,-1,0]
        dc=[0,-1,-1,-1,0,1,1,1,0]
        r,c=self.position
        while (True):
            dir=random.randint(0,len(dr)-1)
            if (inside(r+dr[dir],c+dc[dir]) and environment.board[r+dr[dir]][c+dc[dir]] != 1):
                return [r+dr[dir],c+dc[dir]]
            else:
                dr.pop(dir)
                dc.pop(dir)
        return [0,0]
        
    # If you want a random goal, let goal=None
    def moveGoalAStar(self, environment, seekerInSight, goal=None):
        nr, nc=[environment.rows, environment.columns]

        def inside (r, c):    
            return r>=0 and r<nr and c>=0 and c<nc
        def iswall (r, c):
            return environment.board[r][c] == 1
        
        dr=[-1,0,1,1,1,0,-1,-1]
        dc=[0,-1,-1,-1,0,1,1,1]
        def heuristic (x, y, xp, yp):
            return max(abs(x-xp), abs(y-yp))

        def direct_to_goal (init, goal):
            gr, gc = goal
            r,c = init
            init_r, init_c = init
            # Now A Star to goal      
            parent=[]; cost=[]
            frontier=[]

            for i in range(nr):
                tmp=[]; tmp2=[]
                for j in range(nc):
                    tmp.append([]); tmp2.append(999999)
                parent.append(tmp); cost.append(tmp2)

            cost[r][c]=0; frontier.append([r,c])

            def deadend():
                return parent[gr][gc] != []

            # Cost is g
            while (frontier!=[] and not deadend()):
                Min=999999
                r,c=frontier[0];i=0
                for j in range(len(frontier)):
                    f=frontier[j]
                    if (cost[f[0]][f[1]]+heuristic(f[0],f[1],gr,gc) < Min):
                        Min=cost[f[0]][f[1]]+heuristic(f[0],f[1],gr,gc)
                        r,c=f
                        i=j
                frontier.pop(i)

                for k in range(len(dr)):
                    rr=r+dr[k]; cc=c+dc[k]
                    if inside(rr,cc) and not iswall(rr,cc) and cost[r][c]+1 < cost[rr][cc]:
                        cost[rr][cc]=cost[r][c]+1
                        parent[rr][cc]=[r,c]
                        frontier.append([rr,cc])
            
            if (parent[gr][gc] == []):  # No way to reach goal
                return [-1,-1]    # Continue finding another goal
            trace_x,trace_y = [gr, gc]
            save_x = -1; save_y = -1
            while True:
                save_x, save_y = parent[trace_x][trace_y]
                if save_x == init_r and save_y == init_c:
                    break
                trace_x = save_x; trace_y = save_y

            return [trace_x,trace_y]

        def findGoal ():
            while True :
                r=random.randint(0,nr-1); c=random.randint(0,nc-1)
                if not iswall(r,c):
                    return [r,c]

        if (self.moveGoal_goal is None) or self.position==self.moveGoal_goal:
            if goal is None: # Random goal
                while True:
                    self.moveGoal_goal = findGoal()
                    if (self.position == self.moveGoal_goal):
                        continue
                    if direct_to_goal(self.position, self.moveGoal_goal) != [-1,-1]:
                        #print("Hider next goal: ",str(self.moveGoal_goal))
                        break
            else:
                self.moveGoal_goal = goal
        if self.position != self.moveGoal_goal:
            return direct_to_goal(self.position, self.moveGoal_goal)
        else:
            return self.position

    def moveTacticV1 (self, environment, seekerInSight, obstacleArray):

        if self.tactic_v1 is None:
            self.tactic_v1 = TacticV1(environment, obstacleArray)
        return self.tactic_v1.move(self,environment,seekerInSight,obstacleArray)

class TacticV1: # Now don't use obstacleArray yet
    def __init__ (self, environment, obstacleArray):
        self.nr=environment.rows
        self.nc=environment.columns
        self.map=environment.board # No attempt to change map allowed.
        self.numMoveSinceSeekerInSight = 0
        self.lastKnownSeekerLocation = []
        
        self.mapDeadEnd=[[0 for j in range(self.nc)] for i in range(self.nr)]
        self.mapMerriable=[[0 for j in range(self.nc)] for i in range(self.nr)]
        # self.goalEval=[[0 for j in range(self.nc)] for i in range(self.nr)]

        self.mapReachable=[[0 for j in range(self.nc)] for i in range(self.nr)]
        self.dr8=[-1,-1,0,1,1,1,0,-1]
        self.dc8=[0,-1,-1,-1,0,1,1,1]
        self.dr4=[-1,0,1,0]
        self.dc4=[0,-1,0,1]
        self.generateMapDeadEnd(obstacleArray)
        self.generateMapMerriable(environment, obstacleArray)
    def generateMapReachable (self, pos, environment, obstacleArrayNowNotProcessed):
        visit=[[0 for j in range(self.nc)] for i in range(self.nr)]
        def fill (r,c,fillval):
            if not self.inside(r,c) or visit[r][c] == 1 or environment.board[r][c]==1:
                return
            visit[r][c] = 1
            self.mapReachable[r][c] = fillval
            for i in range(len(self.dr8)):
                rr, cc = [r+self.dr8[i], c+self.dc8[i]]
                fill(rr,cc,fillval)
        fill(pos[0], pos[1], 1)

    def generateMapDeadEnd (self, obstacleArrayNowNotProcessed):
        def inside (r,c):
            return r>=0 and r<self.nr and c>=0 and c<self.nc
        def deadScore (pos):
            ans=0
            for i in range(len(self.dr8)):
                r,c=[pos[0]+self.dr8[i], pos[1]+self.dc8[i]]
                if not inside(r,c):
                    ans+=1
                else:
                    if self.map[r][c]==1 or self.mapDeadEnd[r][c]==1:
                        ans+=1
            return ans
        def deadScore4dir (pos):
            ans=0
            for i in range(len(self.dr4)):
                r,c=[pos[0]+self.dr4[i], pos[1]+self.dc4[i]]
                if not inside(r,c):
                    ans+=1
                else:
                    if self.map[r][c]==1 or self.mapDeadEnd[r][c]==1:
                        ans+=1
            return ans
        def deadCell (pos):
            return (deadScore(pos)>=7) or (deadScore(pos)>=6 and deadScore4dir(pos)>=3)

        visit=[[0 for j in range(self.nc)] for i in range(self.nr)]
        q=Queue()
        for i in range(self.nr):
            for j in range(self.nc):
                if deadCell([i,j]) and self.map[i][j]==0:
                    self.mapDeadEnd[i][j] = 1
                    visit[i][j]=1
                    q.put([i,j])
        # BFS the dead cells
        while not q.empty():
            r,c = q.get()
            for i in range(len(self.dr4)):
                rr, cc = [r+self.dr4[i], c+self.dc4[i]]
                if inside(rr,cc) and self.map[rr][cc]==0 and deadCell([rr,cc]) and visit[rr][cc]==0:
                    self.mapDeadEnd[rr][cc]=1
                    visit[rr][cc]=1
                    q.put([rr,cc])
        return None
    def inside (self,r,c):
        return r>=0 and r<self.nr and c>=0 and c<self.nc
    def generateMapMerriable (self, environment, obstacleArrayNowNotProcessed):
        visit=[[0 for j in range(self.nc)] for i in range(self.nr)]
        compo=[[0 for j in range(self.nc)] for i in range(self.nr)]

        lst_compo=[]
        def fill (r,c,fillval):
            if not self.inside(r,c) or visit[r][c] == 1:
                return
            if self.map[r][c] == 1:
                visit[r][c] = 1
                compo[r][c] = fillval
                lst_compo.append([r,c])
                fill(r-1,c,fillval)
                fill(r,c-1,fillval)
                fill(r+1,c,fillval)
                fill(r,c+1,fillval)

        # Return [] if no route found, otherwise [[x1,y1], [x2,y2], ...]
        # Crude route around a wall component
        def crudeRoute (fillval):
            def strictNeighborOfOne (r, c): # Not itself
                for i in range(len(self.dr8)):
                    rr=r+self.dr8[i]; cc=c+self.dc8[i]
                    if self.inside(rr,cc) and compo[rr][cc]==fillval:
                        return True
                return False
            """
            Algorithm:
            1. Find top-left cell TL
            2. Go 4-dir in order of right, down, left, up, greedily.
                Never go into dead-end cells
                If can't go, then no crude route is found
                If last cell is TL, then crude route found
            """
            TL=[0,0]
            for i in range(self.nr):
                foundTL=False
                for j in range(self.nc):
                    if strictNeighborOfOne(i,j):
                        TL=[i,j]
                        foundTL=True
                        break
                if foundTL:
                    break

            route=[]
            cur=TL; dr=[0,1,0,-1]; dc=[1,0,-1,0] # Order of dr and dc somehow important
            while True:
                route.append(cur)
                foundNxt=False
                for i in range(len(dr)):
                    nxt=[cur[0]+dr[i], cur[1]+dc[i]]
                    if self.inside(nxt[0], nxt[1]) and self.map[nxt[0]][nxt[1]]==0 \
                        and self.mapDeadEnd[nxt[0]][nxt[1]]==0 and (not nxt in route) \
                        and strictNeighborOfOne(nxt[0],nxt[1]):
                        foundNxt=True
                        cur=nxt
                        break
                if not foundNxt:
                    break
            # 4 dir checking if cur is next to TL
            if abs(cur[0]-TL[0])+abs(cur[1]-TL[1]) == 1:
                return route
            else:
                return []

        # Refine with length = 2 only
        def refineRoute_v1 (route):
            while True:
                improved=False
                n=len(route)
                for i in range(n):
                    j=(i+2)%n
                    if max(abs(route[i][0]-route[j][0]), abs(route[i][1]-route[j][1]))<2:
                        improved=True
                        route.pop((i+1)%n)
                        break
                if not improved:
                    break
            return route

        ncompo=0
        for i in range(self.nr):
            for j in range(self.nc):
                if visit[i][j]==0 and self.map[i][j]==1:
                    ncompo += 1
                    fill(i,j,ncompo)
                    rt=crudeRoute(ncompo)
                    rt=refineRoute_v1(rt)
                    for cell in rt:
                        self.mapMerriable[cell[0]][cell[1]]=1

    def beingChased (self):
        return self.lastKnownSeekerLocation!=[] and self.numMoveSinceSeekerInSight <= 3
    def merriableGoal(self):
        return []

    # Tham lam hướng xa seeker nhất mà ít tường nhất
    def greedyDirection(self, hider, seekerpos, obstacleArray):
        BONUS_MORE_DISTANCE = 100
        BONUS_FAVOR_TERRAIN = 1

        dr9=copy.deepcopy(self.dr8)
        dc9=copy.deepcopy(self.dc8)
        dr9.append(0); dc9.append(0)
        
        def distance (A, B):
            return max(abs(A[0]-B[0]), abs(A[1]-B[1]))
        def num_plain_neighbor (r, c):
            ans = 0
            for i in range(len(self.dr8)):
                rr, cc = [r+self.dr8[i], c+self.dr8[i]]
                if self.inside(rr, cc) and self.map[rr][cc]==0:
                    ans += 1
            return ans
        def total_score (pos):
            return distance(pos, seekerpos)*BONUS_MORE_DISTANCE + \
                num_plain_neighbor(pos[0],pos[1])*BONUS_FAVOR_TERRAIN
        
        Max=0; pos=hider.position; save_pos=pos
        for i in range(len(dr9)):
            tmp = [pos[0]+dr9[i], pos[1]+dc9[i]]
            if self.inside(tmp[0],tmp[1]) and self.map[tmp[0]][tmp[1]]==0:
                if total_score(tmp) > Max:
                    Max = total_score(tmp)
                    save_pos = tmp
        return save_pos
        
    def merry_go_round (self, hider, seekerpos, obstacleArray):

        BONUS_AWAY_FROM_SEEKER = 1000
        BONUS_DIAGONAL = 5  # Favor diagonal than UDLR direction
        BONUS_PLAIN_NEIGHBOR = 1 # Favor most-walled (bc merry-go-round)

        dr9=copy.deepcopy(self.dr8)
        dc9=copy.deepcopy(self.dc8)
        dr9.append(0); dc9.append(0)

        # Shuffle to make it random between ties
        dxy = list(zip(dr9, dc9))
        random.shuffle(dxy)
        for i in range(len(dxy)):
            dr9[i]=dxy[i][0]; dc9[i]=dxy[i][1]
        
        def distance (A, B):
            return max(abs(A[0]-B[0]), abs(A[1]-B[1]))
        def terrain_score (r, c):
            ans = 0
            for i in range(len(self.dr8)):
                rr, cc = [r+self.dr8[i], c+self.dr8[i]]
                if self.inside(rr, cc) and self.map[rr][cc]==0:
                    ans += BONUS_PLAIN_NEIGHBOR
            return ans
        def total_eval (pos, attempt):
            ans=distance(attempt,seekerpos)*BONUS_AWAY_FROM_SEEKER
            if min(abs(pos[0]-attempt[0]), abs(pos[1]-attempt[1]))==1:
                ans += BONUS_DIAGONAL
            ans += terrain_score(attempt[0], attempt[1])
            return ans
        
        Max=0; pos=hider.position; save_pos=pos
        for i in range(len(dr9)):
            tmp = [pos[0]+dr9[i], pos[1]+dc9[i]]
            if self.inside(tmp[0],tmp[1]) and self.map[tmp[0]][tmp[1]]==0 \
                and self.mapMerriable[tmp[0]][tmp[1]]==1:
                if total_eval(pos, tmp) > Max:
                    Max = total_eval(pos,tmp)
                    save_pos = tmp
        return save_pos

    def normalGoal (self, hider, obstacleArray, environment, seekerInSight):
        # Merriable > Plain > "Corner" > sidewall > deadend
        # The nearer, the better
        # Favor most walled Merriable, least walled unmerriable
        BONUS_MERRIABLE = 1000
        BONUS_PLAIN_NEIGHBOR = 10
        PENALTY_DEADEND = 1000000
        PENALTY_HEURISTIC_DISTANCE = 3
        PENALTY_HEURISTIC_DISTANCE_DEADEND = 50
        PENALTY_UNREACHABLE = 100000000

        goalEval=[[0 for j in range(self.nc)] for i in range(self.nr)]
        pos=hider.position
        def terrain_score (r, c):
            ans = 0
            for i in range(len(self.dr8)):
                rr, cc = [r+self.dr8[i], c+self.dr8[i]]
                if self.inside(rr, cc) and self.map[rr][cc]==0:
                    ans += BONUS_PLAIN_NEIGHBOR
            return ans
        
        def distance_score (r1, c1, r2, c2):
            dis = max(abs(r1-r2), abs(c1-c2))
            return dis
        self.generateMapReachable(pos, environment, obstacleArray)

        Max=-999999999999; save_goal=pos
        for i in range(self.nr):
            for j in range(self.nc):
                if self.mapReachable[i][j] == 0:
                    goalEval[i][j] -= PENALTY_UNREACHABLE
                if self.mapMerriable[i][j] == 1:
                    goalEval[i][j] += BONUS_MERRIABLE
                    # For merriable, more-walled is better
                    goalEval[i][j] -= terrain_score(i,j)
                else:
                    goalEval[i][j] += terrain_score(i,j)
                if self.mapDeadEnd[i][j] == 1:
                    goalEval[i][j] -= PENALTY_DEADEND
                    # Penalty distance more
                    goalEval[i][j] -= PENALTY_HEURISTIC_DISTANCE_DEADEND * distance_score(i,j,pos[0],pos[1])
                
                goalEval[i][j] -= PENALTY_HEURISTIC_DISTANCE * distance_score(i,j,pos[0],pos[1])

                if (environment.board[i][j]==0 and goalEval[i][j] > Max):
                    Max=goalEval[i][j]
                    save_goal=[i,j]
        return hider.moveGoalAStar(environment, seekerInSight, save_goal)


    def move (self, hider, environment, seekerInSight, obstacleArray): # Refer to flow chart tactic V1
        if (seekerInSight is not None):
            self.numMoveSinceSeekerInSight = 0
            self.lastKnownSeekerLocation = seekerInSight
        else:
            self.numMoveSinceSeekerInSight += 1
        
        if self.beingChased ():
            if self.mapMerriable[hider.position[0]][hider.position[1]] == 1:
                return self.merry_go_round(hider, self.lastKnownSeekerLocation, obstacleArray)
            tmp = self.merriableGoal()
            if (tmp != []):
                return hider.moveGoalAStar(environment, seekerInSight, tmp) # A* direct to goal
            return self.greedyDirection(hider, self.lastKnownSeekerLocation, obstacleArray)
        else:
            return self.normalGoal(hider, obstacleArray, environment, seekerInSight)

    # Be sure to call generateMapReachable before
    def numUnreachableCell (self):
        ans=0
        for i in range(self.nr):
            for j in range(self.nc):
                if self.mapReachable[i][j] == 0:
                    ans+=1
        return ans

    def numDeadendCell (self):
        ans=0
        for i in range(self.nr):
            for j in range(self.nc):
                if self.mapDeadEnd[i][j] == 1:
                    ans+=1
        return ans

    def numMerriableCell (self):
        ans=0
        for i in range(self.nr):
            for j in range(self.nc):
                if self.mapMerriable[i][j] == 1:
                    ans+=1
        return ans