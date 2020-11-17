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

    def play(self):
        pass