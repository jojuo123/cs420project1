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
import random


# Define some colors
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0 , 255)
DARK_GREY = (128, 128, 128)
PINK = (255, 192, 203)
LIGHT_CYAN = (224,255,255)
WOOD = (202,164,114)
used_color = []
used_color.append([4,BLACK]) ; used_color.append([0,WHITE]) ; used_color.append([2,GREEN]) ; used_color.append([3,RED]) ;
used_color.append([1, DARK_GREY]) ; used_color.append([5,PINK]) ; used_color.append([6,LIGHT_CYAN]) ; used_color.append([7,WOOD]) ; 

#gameplay constant
MAP_FILE = ""
MAX_WAIT_TIME = 0.1
TURN_LIMIT = 2000
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

def get_new_color():
    old_color = True
    while (old_color):
        red = random.randint(100,230) ; green = random.randint(100,230) ; blue = random.randint(100,230)
        old_color = False
        for i in range(len(used_color)):
            if red < used_color[i][1][0]*0.5 and red > used_color[i][1][0]*1.5 and green < used_color[i][1][1]*0.5 and green > used_color[i][1][1]*1.5 and blue < used_color[i][1][2]*0.5 and blue > used_color[i][1][2]*1.5:
                old_color = True
                break
    used_color.append([len(used_color),(red,green,blue)])
    return (red,green,blue)

def import_map(file_name):
    file = open(file_name,"r")
    lines = file.readlines()

    data = []
    for line in lines:
        number_strings = line.split() # Split the line on runs of whitespace
        numbers = [int(n) for n in number_strings] # Convert to integers
        data.append(numbers) # Add the "row" to your list.
    total_row = data[0][0]
    total_column = data[0][1]
    data.pop(0)
    file.close()
    hiders = []
    seeker = 0
    obs_list = []
    checked_obs = np.zeros((total_row,total_column))
    for i in range(total_row):
        for j in range(total_column):
            if data[i][j] == 3: #seeker pos
                seeker = seek.Seeker(i,j,3,5)
                data[i][j] = 0
            elif data[i][j] == 2: #hider pos
                hiders.append(hide.Hider(i,j,2))
                data[i][j] = 0

    for i in range(total_row, len(data)):
        new_color = get_new_color()

        obs_ = obs.Obstacle([data[i][0],data[i][1]],[data[i][2]-data[i][0]+1,data[i][3]-data[i][1]+1],new_color)
        obs_list.append(obs_)
    while len(data) > total_row:
        data.pop(total_row)
    return total_row, total_column, data,seeker,hiders,obs_list

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
        board[seeker.position[0]][seeker.position[1]] = 3 #might be corrected later
    #else:
    #    print("invalid seeker coordinate " + str(seeker.position[0]) + ' ' + str(seeker.position[1]))
    for i in range(len(hider)):
        if check_valid_coor(board,hider[i].position[0],hider[i].position[1]):
            board[hider[i].position[0]][hider[i].position[1]] = 2 #might be corrected later
        #else:
        #    print("invalid hider coordinate " + str(hider[i].position[0]) + ' ' + str(hider[i].position[1]))
    return board

def get_color_code(color_to_find):
    for i in range(len(used_color)):
        if color_to_find == used_color[i][1]:
            return i
    return -1

def visualize_obstacles(board,obs_list):
    for i in range(len(obs_list)):
        color_code = get_color_code(obs_list[i].color)
        for j in range(obs_list[i].size[0]):
            for k in range(obs_list[i].size[1]):
                if check_valid_coor(board,obs_list[i].upperLeft[0]+j, obs_list[i].upperLeft[1]+k):
                    board[obs_list[i].upperLeft[0]+j][obs_list[i].upperLeft[1]+k] = color_code #might be corrected later
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
    visual_map = visualize_obstacles(visual_map,engine.obstacles)
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

def get_key(element):
    return element[0]

if __name__=='__main__':
    # init necessary components
    used_color.sort(key = get_key)
    visual_map = []
    total_row = 0
    total_column = 0
    MAP_FILE, engine_level = get_file()

    #lay map tu file 'map.txt'
    total_row, total_column, board, seeker, hiders,obs_list = import_map(MAP_FILE)
    environment = env.Environment(board, total_row, total_column)
    #khoi tao hider va seeker
    #hiders = []
    #seeker = seek.Seeker(0, 1, 3, 5)
    #hiders.append(hide.Hider(0, 0, 3))
    #hiders.append(hide.Hider(29, 26, 3))
    #khoi tao engine
    engine = eng.Engine(environment=environment, hiders=hiders, seeker=seeker,obstacles = obs_list)
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
        seenable = engine.seeker.getVision(engine.environment, engine.obstacles)
        for i in range(len(seenable)):
                for j in range(len(seenable[0])):
                    if visual_map[i][j] == 0 and seenable[i][j] == 1:
                        visual_map[i][j] = 5
        
        #hider vision
        for i in range(len(engine.hiders)):
            seenable = engine.hiders[i].getVision(engine.environment, engine.obstacles)
            for i in range(len(seenable)):
                    for j in range(len(seenable[0])):
                        if visual_map[i][j] == 0 and seenable[i][j] == 1:
                            visual_map[i][j] = 6

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
                #color = WHITE
                #if visual_map[row][column] == 1:
                #    color = DARK_GREY
                #elif visual_map[row][column] == 3:
                #    color = RED
                #elif visual_map[row][column] == 2:
                #    color = GREEN
                #elif visual_map[row][column] == 4:
                #    color = WOOD
                #elif visual_map[row][column] == 998:
                #    color = PINK
                #elif visual_map[row][column] == 999:
                #    color = LIGHT_CYAN
                color = used_color[visual_map[row][column]][1]
                pygame.draw.rect(screen,
                                color,
                                [(MARGIN + WIDTH) * column + MARGIN,
                                (MARGIN + HEIGHT) * row + MARGIN,
                                WIDTH,
                                HEIGHT])
        
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
        # Be IDLE friendly. If you forget this line, the program will 'hang'
        # on exit.
    pygame.quit()



