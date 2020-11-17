import Agent as ag

class Hider(ag.Agent):
    def __init__(self, position, sight):
        ag.__init__(self, position, sight)
    
    def Dead(self):
        self.position = [-1, -1]
    
    def move(self, environment, visionArray):
        pass

    