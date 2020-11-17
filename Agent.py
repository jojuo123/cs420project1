import copy
import Environment

class Agent:
    def __init__(self, position, sight):
        self.position = copy.deepcopy(position)
        self.sight = sight #chi so tam nhin
    
    def move(self, probability):
        pass

    def push(self):
        pass

    def getVision(self, environment):
        #return mang 2d {0,1} 
        #0 la ko co sight
        #1 la co sight
        pass