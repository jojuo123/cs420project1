import Environment as env
import Agent as ag
import Hider as hide 
import Seeker as seek
import copy

class Engine:
    def __init__(self, environment, hiders, seeker):
        self.environment = copy.deepcopy(environment)
        self.seeker = copy.deepcopy(seeker)
        self.hiders = copy.deepcopy(hiders)
        self.score = 0
        self.turn = 0
        self.announceList = []
        self.level = 1

    def setLevel(self, level):
        self.level = level

    def checkDie(self, seeker, hider):
        return seeker.position == hider.position

    def showSight(self, visionMap, isSeeker):
        result = []
        if isSeeker:
            for hider in self.hiders:
                if hider.position == [-1, -1]:
                    continue
                if visionMap[hider.position[0]][hider.position[1]] == 1:
                    result.append(copy.deepcopy(hider.position))
        else:
            if visionMap[self.seeker.position[0]][self.seeker.position[1]] == 1:
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
        seekVision = self.seeker.getVision(self.environment)
        hiderInSight = self.showSight(seekVision, isSeeker=True)
        #print(hiderInSight)
        hiderSound = self.showAnnounce(self.announceList, self.seeker.position, self.seeker.soundRange)

        seekerNextPosition = self.seeker.move(self.environment, hiderSound, hiderInSight)
        #print(self.turn, seekerNextPosition)
        if not seekerNextPosition is None:
            self.seeker.position = copy.deepcopy(seekerNextPosition)
            #print(self.seeker.position)
        self.announceList = []
        for hider in self.hiders:
            if self.checkDie(self.seeker, hider):
                hider.Dead()
                self.UpdateScore(True)
                continue
            hiderVision = hider.getVision(self.environment)
            seekerInSight = self.showSight(visionMap=hiderVision, isSeeker=False)
            #nextPosition = copy.deepcopy(hider.move(...))
            announcePosition = hider.Announce()
            if not announcePosition is None:
                self.announceList.append(copy.deepcopy(announcePosition))

    def isEnd(self):
        for hider in self.hiders:
            if hider.position != [-1, -1]:
                return False
        return True
