import Agent as ag
import random

class Hider(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        self.prob = 0.0
        self.moveRandomGoal_goal = None
        super().__init__(positionx, positiony, sight)
    
    def Dead(self):
        x = self.position[0]
        y = self.position[1]
        self.position = [-1, -1]
        return x,y
    
    def AnnouncePosition(self):
        return self.position
    
    def Announce(self):
        if self.prob >= 0.1:
            m = random.random()
            if m < self.prob:
                self.prob = 0
                return self.AnnouncePosition()
            else:
                self.prob = min(self.prob + 0.1, 1.0)
                return None
        else:
            self.prob = self.prob + 0.1
            return None
    
    def moveProb(self, seekerInSight):
        if (seekerInSight == []):
            return 1.0
        return 0.6
    
    def move(self, environment, seekerInSight):
        p = self.moveProb(seekerInSight)

        def canMove (prob):
            rnd=random.random()
            return rnd<prob
        if not canMove(prob=p):     # Hider won't move this turn
            return None

        #return self.moveRandomDirection (environment, seekerInSight) # Now move random
        return self.moveRandomGoalAStar (environment, seekerInSight)

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
        

    def moveRandomGoalAStar(self, environment, seekerInSight):
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

        if (self.moveRandomGoal_goal is None) or self.position==self.moveRandomGoal_goal:
            while True:
                self.moveRandomGoal_goal = findGoal()
                if (self.position == self.moveRandomGoal_goal):
                    continue
                if direct_to_goal(self.position, self.moveRandomGoal_goal) != [-1,-1]:
                    #print("Hider next goal: ",str(self.moveRandomGoal_goal))
                    break
        return direct_to_goal(self.position, self.moveRandomGoal_goal)
