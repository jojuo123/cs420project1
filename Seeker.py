import Agent as ag

class Seeker(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        self.soundRange = sight
        super().__init__(positionx, positiony, sight)
    
    def __init__(self, positionx, positiony, sight, soundRange):
        self.soundRange = soundRange
        super().__init__(positionx, positiony, sight)
    
    def move(self, environment, announceArray, visionArray):
        pass
    


    