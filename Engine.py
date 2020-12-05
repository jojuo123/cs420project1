import Environment as env
import Agent as ag
import Hider as hide 
import Seeker as seek
import Obstacle as obs
import copy

class Engine:
    def __init__(self, environment, hiders, seeker, obstacles = None):
        self.environment = copy.deepcopy(environment)
        self.seeker = copy.deepcopy(seeker)
        self.hiders = copy.deepcopy(hiders)
        self.score = 1000
        self.turn = 0
        self.announceList = []
        self.level = 1
        self.deadhiders = []
        if obstacles is None:
            self.obstacles = []
        else:
            self.obstacles = obstacles
        
    def TurnLimit(self):
        return self.environment.rows * self.environment.columns * 10

    #hàm này chỉ dành cho level 4
    def TurnLimitForHider(self):
        return 20

    def setLevel(self, level):
        self.level = level

    def checkDie(self, seeker, hider):
        return seeker.position == hider.position

    def showSight(self, visionMap, isSeeker, prevSeekerPosition = None): #prevSeekerPostion chỉ có nghĩa khi isSeeker = False
        result = []
        if isSeeker:
            for hider in self.hiders:
                if hider.position == [-1, -1]:
                    continue
                if visionMap[hider.position[0]][hider.position[1]] == 1:
                    result.append(copy.deepcopy(hider.position))
        else:
            if visionMap[prevSeekerPosition[0]][prevSeekerPosition[1]] == 1:
                result = copy.deepcopy(self.seeker.position)
            else:
                return None
        return result
    
    def showAnnounce(self, announceList, seekerPosition, seekerSoundRange):
        result = []
        for a in announceList:
            maxRange = max(abs(a[0] - seekerPosition[0]), abs(a[1] - seekerPosition[1]))
            if maxRange <= seekerSoundRange:
                result.append(copy.deepcopy(a))
        return result

    def UpdateScore(self, hiderDead = False):
        if not hiderDead:
            self.score -= 1
        else:
            self.score += 20
    
    #hàm này chỉ đánh giá các obs kề với seeker chứ không đánh giá tất cả obs 
    def GetObsAround(self, AgentPosition):
        def isInside(ux, uy, rows, columns):
            return (0 <= ux and ux < rows and 0 <= uy and uy < columns)
        result = []
        if self.obstacles is None:
            return result

        #tạo bảng phụ, với mỗi obstacle i, xem những obs khác i là tường
        tmpboard = copy.deepcopy(self.environment.board)
        for obstacle in self.obstacles:
            for i in range(obstacle.upperLeft[0], obstacle.upperLeft[0] + obstacle.size[0]):
                for j in range(obstacle.upperLeft[1], obstacle.upperLeft[1] + obstacle.size[1]):
                    tmpboard[i][j] = 1
        
        direction = ''
        for obstacle in self.obstacles:
            isMoveable = True
            obstacle.reset_push()
            if (obstacle.upperLeft[0] == AgentPosition[0] - 1) and (obstacle.upperLeft[1] <= AgentPosition[1] <= obstacle.upperLeft[1] + obstacle.size[1] - 1) and (obstacle.size[0] == 1): #up
                for i in range(obstacle.upperLeft[1], obstacle.upperLeft[1] + obstacle.size[1]):
                    if isInside(obstacle.upperLeft[0] - 1, i, self.environment.rows, self.environment.columns):
                        if tmpboard[obstacle.upperLeft[0] - 1][i] == 1:
                            isMoveable = False
                            break
                        for hider in self.hiders:
                            if hider.position == [obstacle.upperLeft[0] - 1, i]:
                                isMoveable = False
                                break
                    else:
                        isMoveable = False
                        break
                if isMoveable:
                    obstacle.up = True
            if (obstacle.upperLeft[0] == AgentPosition[0] + 1) and (obstacle.upperLeft[1] <= AgentPosition[1] <= obstacle.upperLeft[1] + obstacle.size[1] - 1) and (obstacle.size[0] == 1): #down
                for i in range(obstacle.upperLeft[1], obstacle.upperLeft[1] + obstacle.size[1]):
                    if isInside(obstacle.upperLeft[0] + 1, i, self.environment.rows, self.environment.columns):
                        if tmpboard[obstacle.upperLeft[0] + 1][i] == 1:
                            isMoveable = False
                            break
                        for hider in self.hiders:
                            if hider.position == [obstacle.upperLeft[0] + 1, i]:
                                isMoveable = False
                                break
                    else:
                        isMoveable = False
                        break
                if isMoveable:
                    obstacle.down = True
            if (obstacle.upperLeft[1] == AgentPosition[1] - 1) and (obstacle.upperLeft[0] <= AgentPosition[0] <= obstacle.upperLeft[0] + obstacle.size[0] - 1) and (obstacle.size[1] == 1): #left
                for i in range(obstacle.upperLeft[0], obstacle.upperLeft[0] + obstacle.size[0]):
                    if isInside(i, obstacle.upperLeft[1] - 1, self.environment.rows, self.environment.columns):
                        if tmpboard[i][obstacle.upperLeft[1] - 1] == 1:
                            isMoveable = False
                            break
                        for hider in self.hiders:
                            if hider.position == [i, obstacle.upperLeft[1] - 1]:
                                isMoveable = False
                                break
                    else:
                        isMoveable = False
                        break
                if isMoveable:
                    obstacle.left - True
            if (obstacle.upperLeft[1] == AgentPosition[1] + 1) and (obstacle.upperLeft[0] <= AgentPosition[0] <= obstacle.upperLeft[0] + obstacle.size[0] - 1) and (obstacle.size[1] == 1): #right
                for i in range(obstacle.upperLeft[0], obstacle.upperLeft[0] + obstacle.size[0]):
                    if isInside(i, obstacle.upperLeft[1] + 1, self.environment.rows, self.environment.columns):
                        if tmpboard[i][obstacle.upperLeft[1] + 1] == 1:
                            isMoveable = False
                            break
                        for hider in self.hiders:
                            if hider.position == [i, obstacle.upperLeft[1] + 1]:
                                isMoveable = False
                                break
                    else:
                        isMoveable = False
                        break
                if isMoveable:
                    obstacle.right = True
            if isMoveable:
                result.append(copy.deepcopy(obstacle))
        return result

    #hàm này dành cho những turn ban đầu của hider
    #hàm này cần được thảo luận thêm
    def InitPlayForHider(self):
        if self.level < 4:
            return
        turn = 0
        while (turn < self.TurnLimitForHider()):
            turn += 1
            
    def play(self):
        #self.seeker.move(self.environment, [1, 1], [1, 1, 2])
        #self.turn += 1
        #seekvis = seek.getvision
        #hiderinsight = showhider(seekvis) -> list cac [x, y]
        #hiderSound = showAnnounce(announceList, seek.position, seek.soundrange)
        #seeker.move(env, hiderinsight, hiderSound)
        #announcelist = []
        #for hiders:
        #   if checkDie(): -> ham nay cua Engine
        #       hider.Dead()
        #       updateScore
        #   hidervis = hider.getVision
        #   seekinsight = showseek(hidervis) -> 1 [x, y] hoac None
        #   hider.move(env, seekinsight)
        #   announceList.append(hider.announce(self.turn)) if khac <> None

        self.turn += 1
        self.UpdateScore()
        seekVision = self.seeker.getVision(self.environment, self.obstacles)
        hiderInSight = self.showSight(seekVision, isSeeker=True)
        #print(hiderInSight)
        hiderSound = self.showAnnounce(self.announceList, self.seeker.position, self.seeker.soundRange)
        prevSeekerPosition = copy.deepcopy(self.seeker.position)

        seekerNextPosition = []
        if (self.level == 4):
            pushableObsAround = copy.deepcopy(self.GetObsAround(self.seeker.position))
            newObstaclePositions, seekerNextPosition = self.seeker.moveL4(self.environment, hiderSound, hiderInSight, copy.deepcopy(self.obstacles), pushableObsAround) #deepcopy ở đây là quan trọng
            if not newObstaclePositions is None:
                self.obstacles = copy.deepcopy(newObstaclePositions)
        else:
            seekerNextPosition = self.seeker.move(self.environment, hiderSound, hiderInSight, copy.deepcopy(self.obstacles)) #deepcopy ở đây là quan trọng
  
        #print(self.turn, seekerNextPosition)
        if not seekerNextPosition is None:
            self.seeker.position = copy.deepcopy(seekerNextPosition)
        #print("Seeker move to: ",str(self.seeker.position))
        #print(self.seeker.position)
        self.announceList = []
        for hider in self.hiders:
            if self.checkDie(self.seeker, hider):
                hider.Dead()
                self.UpdateScore(True)
                self.deadhiders.append(hider)
                self.hiders.remove(hider)
                continue
            hiderVision = hider.getVision(self.environment, self.obstacles)
            seekerInSight = self.showSight(visionMap=hiderVision, isSeeker=False, prevSeekerPosition=prevSeekerPosition)

            if (self.level >= 3):
                hiderNextPosition = hider.move(self.environment, seekerInSight, obstacleArray=copy.deepcopy(self.obstacles)) #deepcopy ở đây là quan trọng
                #nextPosition = copy.deepcopy(hider.move(...))
                if not hiderNextPosition is None:
                    hider.position = copy.deepcopy(hiderNextPosition)
                #print("Hider move to: ",str(hider.position))
                #print("Hider position: "+str(hider.position))
                # Check for hider-suicide
                if self.checkDie(self.seeker, hider):
                    hider.Dead()
                    self.UpdateScore(True)
                    self.deadhiders.append(hider)
                    self.hiders.remove(hider)
                    continue
            announcePosition = hider.Announce(self.environment, self.obstacles)
            if not announcePosition is None:
                #print ("Hider announce at: "+str(announcePosition))
                self.announceList.append(copy.deepcopy(announcePosition))

    def isEnd(self):
        # if self.TurnLimit() <= self.turn:
        #    return True
        for hider in self.hiders:
            if hider.position != [-1, -1]:
                return False
        return True
