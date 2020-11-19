import Engine as eng
import pygame
import copy

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

def check_valid_coor(board,x,y):
    max_row = len(board)
    max_column = len(board[0])
    if x < 0 or x > max_row:
        return False
    if y < 0 or y > max_column:
        return False
    return True

def visualize_agents(board,seeker,hider):
    if check_valid_coor(board,seeker[0],seeker[1]):
        board[seeker[0]][seeker[1]] = 1 #might be corrected later
    else:
        print("invalid coordinate " + str(seeker[0]) + ' ' + str(seeker[1]))
    for i in range(len(hider)):
        if check_valid_coor(board,hider[i][0],hider[i][1]):
            board[hider[i][0]][hider[i][1]] = 2 #might be corrected later
        else:
            print("invalid coordinate " + str(hider[i][0]) + ' ' + str(hider[i][1]))
    return board

def update_visual_map(engine):
    visual_map = []
    visual_map = copy.deepcopy(engine.environment.board)
    visual_map = visualize_agents(visual_map,engine.seeker,engine.hider)
    return visual_map

if __name__=='__main__':
    # init necessary components
    visual_map = []
    total_row = 0
    total_column = 0
    visual_map = update_visual_map(engine) #engine required !!!
    total_row = len(visual_map)
    total_column = len(visual_map[0])

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

    while not done:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
 
    # Set the screen background
    screen.fill(BLACK)
 
    # Draw the visual_map
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
 
    # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

