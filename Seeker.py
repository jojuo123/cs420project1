import Agent as ag

class Seeker(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        self.soundRange = sight
        super().__init__(positionx, positiony, sight)
    
    #def __init__(self, positionx, positiony, sight, soundRange):
     #   self.soundRange = soundRange
      #  super().__init__(positionx, positiony, sight)
    
    def move(self, environment, announceArray, visionArray):
        pass
    
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
    