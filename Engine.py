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

    def checkDie(self, seeker, hider):
        return seeker.position == hider.position

    def play(self):
        self.seeker.move(self.environment, [1, 1], [1, 1, 2])
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

    def isEnd(self):
        for hider in self.Hiders:
            if hider.position != [-1, -1]:
                return False
        return True
