import Environment as env
import Agent as ag
import Hider as hide 
import Seeker as seek
import Engine as eng
import pygame
import copy
import thanh_heuristic
import time
import numpy as np
import os
import Obstacle as obs


# Define some colors
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0 , 255)
DARK_GREY = (128, 128, 128)
PINK = (255, 192, 203)
LIGHT_GREEN = (152,251,152)
LIGHT_CYAN = (224,255,255)
WOOD = (202,164,114)
#gameplay constant
MAP_FILE = ""
MAX_WAIT_TIME = 0
TURN_LIMIT = 200
TIME_LIMIT = 200
CURRENT_TURN = 0
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20

# This sets the margin between each cell
MARGIN = 1

def get_file():
    file_name = "map/level"
    level = int(input("choose level: "))
    
    file_name += str(level) + '/'
    entries = os.listdir(file_name)

    for i in range(len(entries)):
        print(i+1, entries[i])
    file_num = int(input("choose file number: "))
    file_name += entries[file_num-1]
    
    return file_name,level

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
    hiders = []
    seeker = 0
    for i in range(total_row):
        for j in range(total_column):
            if data[i][j] == 2: #seeker pos
                seeker = seek.Seeker(i,j,3,5)
                data[i][j] = 0
            elif data[i][j] == 3: #hider pos
                hiders.append(hide.Hider(i,j,2))
                data[i][j] = 0

    return total_row, total_column, data,seeker,hiders

def check_valid_coor(board,x,y):
    total_row = len(board)
    total_column = len(board[0])
    if x < 0 or x >= total_row:
        return False
    if y < 0 or y >= total_column:
        return False
    return True

def visualize_agents(board,seeker,hider):
    if check_valid_coor(board,seeker.position[0],seeker.position[1]):
        board[seeker.position[0]][seeker.position[1]] = 2 #might be corrected later
    #else:
    #    print("invalid seeker coordinate " + str(seeker.position[0]) + ' ' + str(seeker.position[1]))
    for i in range(len(hider)):
        if check_valid_coor(board,hider[i].position[0],hider[i].position[1]):
            board[hider[i].position[0]][hider[i].position[1]] = 3 #might be corrected later
        #else:
        #    print("invalid hider coordinate " + str(hider[i].position[0]) + ' ' + str(hider[i].position[1]))
    return board

def visualize_obstacles(board,obs):
    for i in range(len(obs)):
        if check_valid_coor(board,obs[i].position[0],obs[i].position[1]):
            board[obs[i].position[0]][obs[i].position[1]] = 4 #might be corrected later
    return board

def update_visual_map(engine):
    visual_map = []
    row = len(engine.environment.board) ; column = len(engine.environment.board[0])
    for i in range(row):
        temp = []
        for j in range(column):
            temp.append(engine.environment.board[i][j])
        visual_map.append(temp)
    visual_map = visualize_agents(visual_map,engine.seeker,engine.hiders)
    return visual_map

def set_caption(level, time, time_limit, score):
    return "Level: " + str(level) + " Time: " + str(time) + " Time_limit: " + str(time_limit) + 's' + " Score: " + str(score)

def print_summary(level,file_path,status, total_run_time, score, seeker_steps, turn_limit, time_limit):
    print("\n\n\n\n-----------------------------------------------------------------------")
    print("Game status: " + str(status))
    print("Level: " + str(level))
    print("File path: " + str(file_path))
    print("\nTime limit: " + str(time_limit) + 's')
    print("Total run time: " + str(total_run_time))
    print("\nTurn limit: " + str(turn_limit))
    print("Seeker steps: " + str(seeker_steps))
    print("\nSeeker score: " + str(score))
    print("\n\n\n\n\n\n-----------------------------------------------------------------------")



if __name__=='__main__':
    # init necessary components

    visual_map = []
    total_row = 0
    total_column = 0
    MAP_FILE, engine_level = get_file()

    #lay map tu file 'map.txt'
    total_row, total_column, board, seeker, hiders = import_map(MAP_FILE)
    environment = env.Environment(board, total_row, total_column)
    #khoi tao hider va seeker
    #hiders = []
    #seeker = seek.Seeker(0, 1, 3, 5)
    #hiders.append(hide.Hider(0, 0, 3))
    #hiders.append(hide.Hider(29, 26, 3))
    #khoi tao engine
    engine = eng.Engine(environment=environment, hiders=hiders, seeker=seeker)
    engine.setLevel(engine_level)

    visual_map = update_visual_map(engine)

    begin = time.time()
    check_point = begin
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
    timing = time.time()
    debug = True
    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
        if done:
            break
        screen.fill(BLACK)

        visual_map = update_visual_map(engine)
        
        #seeker vision
        seenable = engine.seeker.getVision(engine.environment)
        for i in range(len(seenable)):
                for j in range(len(seenable[0])):
                    if visual_map[i][j] == 0 and seenable[i][j] == 1:
                        visual_map[i][j] = 998
        
        #hider vision
        for i in range(len(engine.hiders)):
            seenable = engine.hiders[i].getVision(engine.environment)
            for i in range(len(seenable)):
                    for j in range(len(seenable[0])):
                        if visual_map[i][j] == 0 and seenable[i][j] == 1:
                            visual_map[i][j] = 999

        #gameplay
        wait_time = time.time() - timing
        if time.time() - timing >= MAX_WAIT_TIME:
            #set caption
            timing = time.time()
            time_passed = str("%.2f" % (time.time() - begin)) + "s"
            score = engine.score
            caption = set_caption(engine_level,time_passed,TIME_LIMIT,score)
            pygame.display.set_caption(caption)

            #engine do
            CURRENT_TURN += 1
            engine.play()
            done = engine.isEnd()
            seeker_score = engine.score
            curr_time = int(time.time() - begin)
            time_passed = str("%.2f" % (time.time() - begin)) + "s"
            if done or CURRENT_TURN >= TURN_LIMIT or curr_time >= TIME_LIMIT:
                if CURRENT_TURN >= TURN_LIMIT:
                    status = "SEEKER RUNS OUT OF TURN"
                elif curr_time >= TIME_LIMIT:
                    status = "SEEKER RUNS OUT OF TIME"
                else:
                    status = "SEEKER COMPLETES THIS ROUND"
                print_summary(engine_level, MAP_FILE, status, time_passed,score,CURRENT_TURN,TURN_LIMIT,TIME_LIMIT)
                done = True
        
        for row in range(total_row):
            for column in range(total_column):
                color = WHITE
                if visual_map[row][column] == 1:
                    color = DARK_GREY
                elif visual_map[row][column] == 2:
                    color = RED
                elif visual_map[row][column] == 3:
                    color = GREEN
                elif visual_map[row][column] == 4:
                    color = WOOD
                elif visual_map[row][column] == 998:
                    color = PINK
                elif visual_map[row][column] == 999:
                    color = LIGHT_CYAN
                pygame.draw.rect(screen,
                                color,
                                [(MARGIN + WIDTH) * column + MARGIN,
                                (MARGIN + HEIGHT) * row + MARGIN,
                                WIDTH,
                                HEIGHT])
        
        # Limit to 60 frames per second
        time.sleep(0.1)
        clock.tick(60)
 
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
    pygame.quit()



