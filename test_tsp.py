import Environment as env
import Agent as ag
import Hider as hide 
import Seeker as seek
import Engine as eng
import pygame
import copy
import time

# Define some colors
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0 , 255)
DARK_GREY = (128, 128, 128)
MAP_FILE = "map.txt"
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 5

def import_map(file_name):
    file = open(file_name,"r")
    total_row = int(file.readline())
    total_column = int(file.readline())
    lines = file.readlines()

    data = []
    for line in lines:
        number_strings = line.split() # Split the line on runs of whitespace
        numbers = [int(n) for n in number_strings] # Convert to integers
        data.append(numbers) # Add the "row" to your list.

    file.close()
    return total_row, total_column, data

def check_valid_coor(board,x,y):
    global total_row, total_column
    if x < 0 or x >= total_row:
        return False
    if y < 0 or y >= total_column:
        return False
    return True

def visualize_agents(board,seeker,hider):
    if check_valid_coor(board,seeker.position[0],seeker.position[1]):
        board[seeker.position[0]][seeker.position[1]] = 2 #might be corrected later
    else:
        print("invalid coordinate " + str(seeker.position[0]) + ' ' + str(seeker.position[1]))
    for i in range(len(hider)):
        if check_valid_coor(board,hider[i].position[0],hider[i].position[1]):
            board[hider[i].position[0]][hider[i].position[1]] = 3 #might be corrected later
        else:
            print("invalid coordinate " + str(hider[i].position[0]) + ' ' + str(hider[i].position[1]))
    return board

def update_visual_map(engine):
    visual_map = []
    visual_map = copy.deepcopy(engine.environment.board)
    visual_map = visualize_agents(visual_map,engine.seeker,engine.hiders)
    return visual_map

if __name__=='__main__':
    # init necessary components
    visual_map = []
    total_row = 0
    total_column = 0

    #lay map tu file 'map.txt'
    total_row, total_column, board = import_map(MAP_FILE)
    environment = env.Environment(board, total_row, total_column)
    #khoi tao hider va seeker
    hiders = []
    seeker = seek.Seeker(3, 4, 5, 5)
    hiders.append(hide.Hider(0, 0, 3))
    hiders.append(hide.Hider(0, 16, 3))
    hiders.append(hide.Hider(0, 19, 3))
    hiders.append(hide.Hider(6, 15, 3))
    hiders.append(hide.Hider(8, 0, 3))
    hiders.append(hide.Hider(10, 10, 3))
    hiders.append(hide.Hider(13, 1, 3))
    hiders.append(hide.Hider(16, 1, 3))
    hiders.append(hide.Hider(16, 5, 3))
    hiders.append(hide.Hider(19, 19, 3))
    #khoi tao engine
    engine = eng.Engine(environment=environment, hiders=hiders, seeker=seeker)

    visual_map = update_visual_map(engine)
    #total_row = len(visual_map)
    #total_column = len(visual_map[0])

    # Initialize pygame
    pygame.init()
 
    # Set the HEIGHT and WIDTH of the screen
    screen_height = total_column*WIDTH + MARGIN*(total_column+1)
    screen_width = total_row*HEIGHT + MARGIN*(total_row+1)
    WINDOW_SIZE = [screen_height, screen_width]
    screen = pygame.display.set_mode(WINDOW_SIZE)
 
    # Set title of screen
    pygame.display.set_caption("hide and seek test")
 
    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    #main loop
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
        if done:
            break
        screen.fill(BLACK)

        visual_map = update_visual_map(engine)
        
        for row in range(total_row):
            for column in range(total_column):
                color = WHITE
                if visual_map[row][column] == 1:
                    color = DARK_GREY
                elif visual_map[row][column] == 2:
                    color = RED
                elif visual_map[row][column] == 3:
                    color = GREEN
                pygame.draw.rect(screen,
                                color,
                                [(MARGIN + WIDTH) * column + MARGIN,
                                (MARGIN + HEIGHT) * row + MARGIN,
                                WIDTH,
                                HEIGHT])
        #gameplay
        engine.play()
        # time.sleep(0.5)
        done = engine.isEnd()
        
    # Limit to 60 frames per second
        clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

