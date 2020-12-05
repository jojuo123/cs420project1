import copy

class Obstacle:
    def __init__(self, upperLeftPosition: list, size: list, color = None):
        self.upperLeft = copy.deepcopy(upperLeftPosition) #[row, col]
        self.size = copy.deepcopy(size)
        self.color = color
        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def reset_push(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False

    def move(self, direction):
        if direction.lower() == 'left':
            self.upperLeft[1] -= 1
        elif direction.lower == 'right':
            self.upperLeft[1] += 1
        elif direction.lower() == 'up':
            self.upperLeft[0] -= 1
        elif direction.lower() == 'down':
            self.upperLeft[0] += 1



    
        