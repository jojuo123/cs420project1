import pygame
import random
import numpy as np
import Obstacle as obs
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0 , 255)
DARK_GREY = (128, 128, 128)
WOOD = (202,164,114)
MAP_FILE = "map/level1/map.txt"
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 1
 
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
grid = []
total_row = 30
total_column = 30

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
    for i in range(total_row):
        for j in range(total_column):
            if data[i][j] == 3: #seeker pos
                data[i][j] = 3
            elif data[i][j] == 2: #hider pos
                data[i][j] = 2

    for i in range(total_row, len(data)):
        obs_ = obs.Obstacle([data[i][0],data[i][1]],[data[i][2]-data[i][0]+1,data[i][3]-data[i][1]+1],WOOD)
        obs_list.append(obs_)
    while len(data) > total_row:
        data.pop(total_row)
    return total_row, total_column, data,seeker,hiders,obs_list

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

def visualize_obstacles(board,obs_list):
    for i in range(len(obs_list)):
        for j in range(obs_list[i].size[0]):
            for k in range(obs_list[i].size[1]):
                board[obs_list[i].upperLeft[0]+j][obs_list[i].upperLeft[1]+k] = 4 #might be corrected later
    return board

def iterate(board):
    checked_obs = np.zeros((total_row,total_column))
    obs_list = []
    for i in range(total_row):
        for j in range(total_column):
            if board[i][j] == 4 and checked_obs[i][j] == 0:
                obs_,checked_obs = find_obs(board,i,j,checked_obs)
                obs_list.append(obs_)
    return obs_list

def find_obs(data,x,y,checked_obs):
    upper_left = [x,y]
    total_row = len(data)
    total_column = len(data[0])
    size_row = 0
    size_col = 0
    xx = x ; yy = y
    while yy < total_column and data[xx][yy] == 4:
        if checked_obs[xx][yy] == 0:
            checked_obs[xx][yy] = 1
            size_col += 1
        yy += 1
    xx = x+1 ; yy = y
    if size_col <= 1:
        size_row = 1
        while xx < total_row and data[xx][yy] == 4:
            if checked_obs[xx][yy] == 0 :
                checked_obs[xx][yy] = 1
                size_row += 1
            xx += 1
        return obs.Obstacle(upper_left,[size_row,size_col],WOOD),checked_obs
    else:
        size_row = 1
        return obs.Obstacle(upper_left,[size_row,size_col],WOOD),checked_obs


def generate_empty_map():

    for row in range(total_row):
        # Add an empty array that will hold each cell
        # in this row
        grid.append([])
        for column in range(total_column):
            if (random.randint(0,2) == 0):
                grid[row].append(1)  # Append a cell
            else:
                grid[row].append(0)

#choose 1 of 2
dump1 = [] ;  dump2 = [];  obs_list = 0
total_row, total_column, grid,dump1, dump2,obs_list = import_map(MAP_FILE)
visualize_obstacles(grid,obs_list)
#generate_empty_map()



# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
#grid[1][5] = 1
 
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

def change_status(cell):
    cell = cell + 1
    if cell == 5:
        cell = 0
    return cell


def export_map(file_name, grid):
    obs_list = iterate(grid)
    file = open(file_name,"w")
    file.write(str(total_row)+ " " + str(total_column) + "\n")
    for row in range(total_row):
        for column in range(total_column):
            if grid[row][column] == 4:
                grid[row][column] = 0
            file.write(str(grid[row][column])+ " ")
        file.write("\n")
    for i in range(len(obs_list)):
        file.write(str(obs_list[i].upperLeft[0]) + ' ' + str(obs_list[i].upperLeft[1]) + ' ' + str(obs_list[i].upperLeft[0]+obs_list[i].size[0]-1) + ' ' + str(obs_list[i].upperLeft[1]+obs_list[i].size[1]-1) + "\n")
    file.close()
 
# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
            export_map(MAP_FILE,grid)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            # Set that location to one
            grid[row][column] = change_status(grid[row][column])
            print("Click ", pos, "Grid coordinates: ", row, column)
 
    # Set the screen background
    screen.fill(BLACK)
 
    # Draw the grid
    for row in range(total_row):
        for column in range(total_column):
            color = WHITE
            if grid[row][column] == 1:
                color = DARK_GREY
            elif grid[row][column] == 3:
                color = RED
            elif grid[row][column] == 2:
                color = GREEN
            elif grid[row][column] == 4:
                color = WOOD
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