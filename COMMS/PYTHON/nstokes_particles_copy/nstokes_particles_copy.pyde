add_library('serial')

import fluid as Fluid
from easing_functions import *
from random import randint 
from time import sleep
# from sinewave import renderWave, calcWave
import math

#SineWave
xspacing = 1     # How far apart should each horizontal location be spaced
theta = 50       # Start angle at 0
amplitude = 23.0    # Height of wave
period = 300.0      # How many pixels before the wave repeats
dx = (TWO_PI / period) * xspacing # Value for incrementing X, a function of period and xspacing
directionX = 0
directionY = 0
counter = 0
angle = 0
toggle = 1
ccounter = 0 
location_tracker = []

#GLOBAL VARIABLES FOR NAVIER_STOKES
WIDTH = 8
D_RATE = 0.1
VISCOSITY = 0.7
TIME_SPACE = 0.0005

#Global GRID 
GRID =[]

FLUID = Fluid.fluid(WIDTH, D_RATE, VISCOSITY, TIME_SPACE)

#Velocity and Density Fields  
SIZE = (WIDTH+2)**2
VEL_HPREV = [0] * SIZE
VEL_H = [0 for _ in xrange(SIZE)]
VEL_VPREV = [0] * SIZE
VEL_V = [0 for _ in xrange(SIZE)]
DENS = [0 for _ in xrange(SIZE)]
DENS_PREV = [0] * SIZE

counter = 0

MOUSE_X = 0
MOUSE_Y = 0

#Serial Connection
upperPort = None
lowerPort = None
img = 0

STARTING = 0
GLOBAL_TIME = 0

#Movements: 
BUBBLE_TOGGLE = False
SNEK_TOGGLE = False
AMOEBA_TOGGLE = False

sf = 100

def snek():
    global w  # Width of entire wave
    w = width + 16
    # Using a list to store height values for the wave.
    global yvalues
    yvalues = [0.0] * (w / xspacing)
    calcWave()
    renderWave()
    
def setup():
    global FLUID, GRID, WIDTH, D_RATE, VISCOSITY, TIME_SPACE, upperPort, lowerPort, img, sf, w, yvalues
    background(0)
    size(WIDTH * sf, WIDTH * sf)
    GRID = makeGrid(WIDTH)

    # frameRate(1000)
    
    w = WIDTH * sf / 3
    yvalues = [0.0] * (w / xspacing)
    
    colorMode(RGB)
    img = loadImage("test.png")

    for i in xrange(WIDTH):
        for j in xrange(WIDTH):
            # DENS[FLUID.xy_coordinate(WIDTH, i, j)] = img.pixels[FLUID.xy_coordinate(WIDTH, i, j)] / 65535 + 256
            DENS[FLUID.xy_coordinate(WIDTH, i, j)] = 0
            # print(img.pixels[FLUID.xy_coordinate(WIDTH, i, j)] / 65535 + 256)
    
    #Port Initialization
    print(Serial.list())
    #Change Port Number as needed
    arduinoPort = Serial.list()[3]
    #Increased Baud Rate to 1Mbs
    magnetPort = Serial(this, arduinoPort, 1000000)
    
def rotate_left():
    global angle, period, xspacing
    angle -= (TWO_PI / period) * xspacing
    print("TURNING LEFT")
    
def rotate_right():
    global angle, period, xspacing
    angle += (TWO_PI / period) * xspacing
    print("TURNING RIGHT")
    
directionxSWITCH = 1
directionySWTICH = 1
    
def draw():
    global counter, GRID, WIDTH, D_RATE, VISCOSITY, TIME_SPACE, VEL_H, VEL_HPREV, VEL_V, VEL_VPREV, DENS, DENS_PREV, img, STARTING, BUBBLE_TOGGLE, GLOBAL_TIME, SNEK_TOGGLE, AMOEBA_TOGGLE, directionX, directionY, amplitude, xspacing, yvalues, toggle, ccounter, theta, location_tracker, sf, angle, period, directionxSWITCH, directionySWTICH
    background(0)
    GLOBAL_TIME += 1
    
    # translate(12,12)
    if(GLOBAL_TIME % 10 == 0):
        VEL_H, VEL_V, VEL_HPREV, VEL_VPREV = FLUID.velocity_step(WIDTH, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, VISCOSITY, TIME_SPACE)
    
        # for i in location_tracker[:50]:
        #     center_x = i[0]
        #     center_y = i[1]
            
        #     DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] -= 50
        #     DENS[FLUID.xy_coordinate(WIDTH, center_x, center_y + 1)] -= 50
        #     DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y)] -= 50
        #     DENS[FLUID.xy_coordinate(WIDTH, center_x + 2, center_y + 1)] -= 50
        #     DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 2)] -= 50
        
        # location_tracker = []
        
    DENS, DENS_PREV = FLUID.density_step(WIDTH, DENS, DENS_PREV, VEL_H, VEL_V, D_RATE, TIME_SPACE) 
    
    # directionX += randint(0,4) * 4
    # directionY -= randint(0,1)
    # calcWave()
    # renderWave()

    
    # if toggle:
    #     amplitude+=4
    #     xspacing-=0.006
    #     ccounter+=1
    #     directionX += 9 * directionxSWITCH
    #     theta += 0.02
    #     # print("contracting")
    #     if ccounter == 20:
    #         toggle = 0
    #         ccounter = 0
    #         if randint(0, 1):
    #             rotate_right()
    #             # if directionxSWITCH:
    #             #     directionxSWITCH *= -1
    #         else:
    #             rotate_left()
            
    # else:
    #     amplitude-=4
    #     xspacing+=0.006
    #     directionX+=10
    #     theta -= 0.04
    #     # print("expanding")
    #     ccounter+=1
    #     if ccounter == 20:
    #         toggle = 1
    #         ccounter = 0 
    
    for i in xrange(WIDTH):
        for j in xrange(WIDTH):
            num = FLUID.xy_coordinate(WIDTH, i, j)
            wind = PVector(VEL_H[num], VEL_V[num])   
            # drawVector(wind, PVector(i * 20, j * 20, 0))
            
    reset_gridcells()
    display_grid()
    
    if (BUBBLE_TOGGLE):
        if(GLOBAL_TIME % 3 == 0):
            DENS = [0 for _ in xrange(SIZE)]
            bubbly()
            carr = new_count()
            # index = 0
            # magnetBufferUpper = "<MAG,"
            # magnetBufferLower = "<MAG,"
            # for i in carr:
            #     index += 1
            #     if index < 8:
            #         magnetBufferUpper += (str(i) + ",")
            #         #magnetBufferUpper += (str(0) + ",")
            #     else:
            #         magnetBufferLower += (str(i) + ",")
            #         #magnetBufferLower += (str(100) + ",")
            # magnetBufferUpper += (">")
            # magnetBufferLower += (">")
        
            # print(magnetBufferUpper + magnetBufferLower)
            # upperPort.write(magnetBufferUpper)
            
    if (SNEK_TOGGLE):
        # if(GLOBAL_TIME % 0 == 0):
        snek()
        carr = new_count()
            # carr = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            # index = 0
            # magnetBufferUpper = "<MAG,"
            # magnetBufferLower = "<MAG,"
            # for i in carr:
            #     index += 1
            #     if index < 8:
            #         magnetBufferUpper += (str(i) + ",")
            #         #magnetBufferUpper += (str(0) + ",")
            #     else:
            #         magnetBufferLower += (str(i) + ",")
            #         #magnetBufferLower += (str(100) + ",")
            # magnetBufferUpper += (">")
            # magnetBufferLower += (">")
        
            # print(magnetBufferUpper + magnetBufferLower)
            # upperPort.write(magnetBufferUpper)
            
    if (AMOEBA_TOGGLE):
        if(GLOBAL_TIME % 22 == 0):
            amoeba()
        if(GLOBAL_TIME % 175 == 0):
            DENS = [0 for _ in xrange(SIZE)]
    
    #Write to Arduino
    START_SEQUENCE = 1
    END_SEQUENCE = 2
    carr = new_count()
    magnetBuffer = "<MAG,"
    
    #Assuming a range of no more then 64 values
    for i in carr:
        magnetPort.write(START_SEQUENCE)
        magnetPort.write(value)
        magnetPort.write(value >> 8)
        magnetBuffer += (str(i) + ",")
        delay(1)

    magnetBufferUpper += (">")
    magnetPort.write(END_SEQUENCE)
    magnetPort.write(100)
    
    # print(magnetBuffer)

#This function counts how many green boxes there are in each quadrant.
def count():
    global VEL_V, VEL_H, WIDTH, FLUID 
    counter = [0,0,0,0]
    for i in range(WIDTH):
        for j in range(WIDTH):
            magnitude = sqrt(VEL_V[FLUID.xy_coordinate(WIDTH, i, j)]**2 + VEL_H[FLUID.xy_coordinate(WIDTH, i, j)]**2)
            if magnitude > 0.2:
                if i < 10 and j < 10:
                    counter[0]+=1
                elif i >= 10 and j < 10:
                    counter[1]+=1
                elif i < 10 and j >= 10:
                    counter[2]+=1
                else:
                    counter[3]+=1
    return counter

def ratio(x):
    if (x * 100 / 256) > 100:
        return 100
    else:
        return (x * 100 / 256)
    
def new_count():
    global DENS, WIDTH, FLUID 
    counter = []
    
    for i in range(WIDTH):
        for j in range(WIDTH):
            counter.append(ratio(DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)]))

    return counter
    
#This function draws green boxes.
def drawVector(v, loc):
    stroke(0, 255, 0)
    if sqrt(abs(v.x)**2 + abs(v.y)**2) > 0.2:
        # noStroke()
        fill(0, 200, 0)
        rect(loc.x, loc.y, 8, 8)
        # line(loc.x, loc.y, loc.x + (v.x), loc.y + (v.y))

#Stores the starting position for the external force. 
def mousePressed():
    global MOUSE_X, MOUSE_Y, VEL_H, VEL_V
    
    MOUSE_X = mouseX
    MOUSE_Y = mouseY

#Adds an external force on the grid.
def mouseReleased():
    global DENS, FLUID, WIDTH, VEL_H, VEL_V, MOUSE_X, MOUSE_Y
    
    magnitude = sqrt((MOUSE_X - mouseX)**2 + (MOUSE_Y - mouseY)**2) / 2
    # print(magnitude)
    center_x = mouseX // sf
    center_y = mouseY // sf
    
    VEL_H[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = (mouseX - MOUSE_X) * magnitude // 2
    VEL_V[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = (mouseY - MOUSE_Y) * magnitude // 2 
    
def mouseDragged():
    redraw()   

def keyPressed():
    global DENS, DENS_PREV, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, BUBBLE_TOGGLE, SNEK_TOGGLE, AMOEBA_TOGGLE, D_RATE
    
    if ((key == 'R') or (key == 'r')):
        DENS = [0 for _ in xrange(SIZE)]
        DENS_PREV = [0 for _ in xrange(SIZE)]
        VEL_H = [0 for _ in xrange(SIZE)]
        VEL_HPREV = [0 for _ in xrange(SIZE)]
        VEL_V = [0 for _ in xrange(SIZE)]
        VEL_VPREV = [0 for _ in xrange(SIZE)]
        
    if ((key == 'D') or (key == 'd')):
        center_x = mouseX // sf
        center_y = mouseY // sf
        
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] -= 10
        
    if ((key == 'F') or (key == 'f')):
        center_x = mouseX // sf
        center_y = mouseY // sf
        
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] += 10
        DENS[FLUID.xy_coordinate(WIDTH, center_x, center_y + 1)] += 10
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y)] += 10
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 2, center_y + 1)] += 10
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 2)] += 10
        
    if ((key == 'B') or (key == 'b')):
        D_RATE = 0.3
        BUBBLE_TOGGLE = not BUBBLE_TOGGLE
        
    if ((key == 'S') or (key == 's')):
        D_RATE = 0.01
        SNEK_TOGGLE = not SNEK_TOGGLE
    
    if ((key == 'A') or (key == 'a')):
        D_RATE = 0.5
        AMOEBA_TOGGLE = not AMOEBA_TOGGLE
        
    if ((key == 'M') or (key == 'm')):
        center_x = mouseX // sf
        center_y = mouseY // sf

        for i in easelist():
            DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = i
        
def bubbly():
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256
    DENS[FLUID.xy_coordinate(WIDTH, randint(0,100) + 1,  randint(0,100) + 1)] = 256

ONCE = False

def amoeba():
    global ONCE, AMOEBA_TOGGLE
    
    VISCOSITY = 1
    
    if not ONCE:
        DENS[FLUID.xy_coordinate(WIDTH, randint(0,3) + 1,  randint(0,3) + 1)] = randint(0,256)
        DENS[FLUID.xy_coordinate(WIDTH, randint(0,3) + 1,  randint(0,3) + 1)] = randint(0,256)
        DENS[FLUID.xy_coordinate(WIDTH, randint(0,3) + 1,  randint(0,3) + 1)] = randint(0,256)
        ONCE = False

def find_neighbors(pos):
    global WIDTH 
    lt = []
    for i in range(pos[0] - 1, pos[0] + 2):
        for j in range(pos[1] - 1, pos[1] + 2):
            if i != 0 and i != WIDTH + 1 and j != 0 and j != WIDTH + 1:
                if (i, j) != SNEK_BODY and (i, j) != SNEK_TAIL and (i, j) != SNEK_HEAD:
                    if abs(SNEK_HEAD[0] - i) + abs(SNEK_HEAD[1] - j) < 2:
                        lt.append((i,j))
    return lt

def reset_gridcells():
    global DENS, WIDTH, GRID
    for i in xrange(WIDTH):
        for j in xrange(WIDTH):
            GRID[i][j] = Cell(i*sf,j*sf,sf, sf, DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)])
    
def makeGrid(wth):
    global GRID 
    for i in xrange(wth):
        # Create an empty list for each row
        GRID.append([])
        for j in xrange(wth):
            # Pad each column in each row with a 0
            GRID[i].append(0)
            
    return GRID

def display_grid():
    global GRID, WIDTH
    for i in xrange(WIDTH):
        for j in xrange(WIDTH):
            if GRID[i][j].tempDens > 0.1:
                # print(GRID[i][j].tempDens)
                GRID[i][j].display()

class Cell():
    def __init__(self, tempX, tempY, tempW, tempH, tempDens):
        self.x = tempX
        self.y = tempY
        self.w = tempW
        self.h = tempH
        self.tempDens = tempDens
        
    def display(self):
        noStroke()
        fill(0, self.tempDens, 0)
        # fill(0, 256, 0)
        # fill(0, 0, 0, 0)
        rect(self.x,self.y,self.w,self.h)
        
def calcWave():
    global theta, directionxSWITCH
    # Increment theta (try different values for 'angular velocity' here
    
    theta += 0.5
    
    # For every x varlue, calculate a y value with sine function
    x = theta
    for i in range(len(yvalues)):
        yvalues[i] = sin(x) * amplitude
        x += dx
        
def renderWave():
    global counter, angle, sf, location_tracker
    noStroke()
    fill(255)
        
    for x in range(len(yvalues)):
        val_x = x * xspacing + directionX
        val_y = (height/2 + yvalues[x]) + directionY
        
        val_x = ((val_x) * (cos(angle)) - (val_y) * (sin(angle))) // sf
        val_y = ((val_x) * (sin(angle)) + (val_y) * (cos(angle))) // sf
        
        DENS[FLUID.xy_coordinate(WIDTH, val_x + 1, val_y + 1)] = 100
        DENS[FLUID.xy_coordinate(WIDTH, val_x, val_y + 1)] = 100
        DENS[FLUID.xy_coordinate(WIDTH, val_x + 1, val_y)] = 100
        DENS[FLUID.xy_coordinate(WIDTH, val_x + 2, val_y + 1)] = 100
        DENS[FLUID.xy_coordinate(WIDTH, val_x + 1, val_y + 2)] = 100
        DENS[FLUID.xy_coordinate(WIDTH, val_x , val_y)] = 100

        location_tracker.append((val_x, val_y))
