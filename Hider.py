import Agent as ag

class Hider(ag.Agent):
    def __init__(self, positionx, positiony, sight):
        super().__init__(positionx, positiony, sight)
    
    def Dead(self):
        self.position = [-1, -1]
    
    def move(self, environment, visionArray):
        pass

    