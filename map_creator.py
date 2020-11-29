import pygame
 
# Define some colors
BLACK = (0, 0, 0)
WHITE = (250, 250, 250)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0 , 255)
DARK_GREY = (128, 128, 128)
MAP_FILE = "map/map2.txt"
 
# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 20
HEIGHT = 20
 
# This sets the margin between each cell
MARGIN = 5
 
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
grid = []
total_row = 20
total_column = 20

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

def generate_empty_map():
    for row in range(total_row):
        # Add an empty array that will hold each cell
        # in this row
        grid.append([])
        for column in range(total_column):
            grid[row].append(0)  # Append a cell

#choose 1 of 2
total_row, total_column, grid = import_map(MAP_FILE)
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
    if cell == 4:
        cell = 0
    return cell

def export_map(file_name, grid):
    file = open(file_name,"w")
    file.write(str(total_row)+"\n")
    file.write(str(total_column)+"\n")
    for row in range(total_row):
        for column in range(total_column):
            file.write(str(grid[row][column])+ " ")
        file.write("\n")
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
            elif grid[row][column] == 2:
                color = RED
            elif grid[row][column] == 3:
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