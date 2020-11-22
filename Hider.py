import Agent as ag
import random

class Hider(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        self.prob = 0.0
        super().__init__(positionx, positiony, sight)
    
    def Dead(self):
        self.position = [-1, -1]
    
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
        return 0.0
    
    def move(self, environment, seekerInSight):
        p = self.moveProb(seekerInSight)
        pass

    