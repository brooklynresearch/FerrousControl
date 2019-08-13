add_library('serial')

import fluid as Fluid
from easing_functions import *
from random import randint 
from time import sleep, time
import math
from threading import Thread
from Queue import Queue

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
WIDTH = 40
sf = 20
D_RATE = 2
VISCOSITY = 0.8
TIME_SPACE = 0.0001

#GLOBAL GRID 
GRID =[]
FLUID = Fluid.fluid(WIDTH, D_RATE, VISCOSITY, TIME_SPACE)

#Velocity and Density Fields
SIZE = (WIDTH+2)**2
VEL_HPREV = [0] * SIZE
VEL_H = [0 for _ in xrange(SIZE)]
VEL_VPREV = [0] * SIZE
VEL_V = [0 for _ in xrange(SIZE)]
DENS = [0 for _ in xrange(SIZE)]
DENS_PREV = [0 for _ in xrange(SIZE)]

counter = 0

#Serial Connection
magnetPort = None
INITIALIZED = False
MAGNET_CONNECTION = False

STARTING = 0

#TOGGLES
AMOEBA_TOGGLE = False
SNEK_TOGGLE = False
EASING_TOGGLE = False
TEST_TOGGLE = False
ON_TOGGLE = False
testIndex = WIDTH + 1 

def genrandi(maxn, num):
    newi = randint(0, maxn)
    while(newi == num):
        newi = randint(0, maxn)
    return newi

#Snake Globals
fcx = randint(0, WIDTH)
fcy = randint(0, WIDTH)
nax = genrandi(WIDTH, fcx)
nay = genrandi(WIDTH, fcy)
scx = randint(0, WIDTH)
scy = randint(0, WIDTH)
nax1 = randint(0, WIDTH)
nay1 = randint(0, WIDTH)

s_tracker = []

def threadSerial(infosend):
    global magnetPort

    if infosend != None:
        magnetPort.write(infosend)

# Send Queue
sendQueue = Queue()
sendThread = Thread(target = threadSerial, args = [None])
busyCount = 0
openCount = 0

#EASING Globals
FadeBox = [0 for _ in range(SIZE)]
ease_range = easelist()
FrameIndex = 0
ease_variable = False 
sign = -1

def reordinator(initial_list):
    reordered_list = []
    
    for panel_y in range(5):
        for panel_x in range(5):
            for quad_y in range(2):
                for quad_x in range(2):
                    for mag_y in range(4):
                        for mag_x in range(4):
                            index = mag_x + mag_y * 40 + quad_x * 4 + quad_y * 160 + panel_x * 8 + panel_y * 320
                            reordered_list.append(initial_list[index])
                            
    return reordered_list

def setup():
    global FLUID, GRID, WIDTH, D_RATE, VISCOSITY, TIME_SPACE, sf, w, yvalues
    background(0)
    size(WIDTH * sf, WIDTH * sf)
    
    #Initializing the Navier Stokes grid.
    GRID = makeGrid(WIDTH)
    
    #Sine Wave variables intialization.
    w = WIDTH * sf / 3
    yvalues = [0.0] * (w / xspacing)
     
    #Generating coordinates for snake movements.
    snake(WIDTH / 3)
    
    frameRate(7)

fr = 30
fc = 0
ptime = time()
rampsign = True

def draw():
    global rampsign, ease_variable, sign, fr, fc, ptime, testIndex, TEST_TOGGLE, EASING_TOGGLE, FrameIndex, FadeBox, ease_range, s_tracker, MAGNET_CONNECTION, INITIALIZED, magnetPort, randposX, randposY, npcounter, counter, GRID, WIDTH, D_RATE, VISCOSITY, TIME_SPACE, VEL_H, VEL_HPREV, VEL_V, VEL_VPREV, DENS, DENS_PREV, STARTING, BUBBLE_TOGGLE, SNEK_TOGGLE, AMOEBA_TOGGLE, directionX, directionY, amplitude, xspacing, yvalues, toggle, ccounter, theta, location_tracker, sf, angle, period, sendThread, busyCount, openCount
    
    background(0)
    
    # if(frameCount % fr == 0):
    #     print(frameCount - fc, time() - ptime)
    #     ptime = time()
    #     fc = frameCount

    if EASING_TOGGLE:
        
        if AMOEBA_TOGGLE == True:
            AMOEBA_TOGGLE = False
            
        if SNEK_TOGGLE == True:
            SNEK_TOGGLE = Fse
        
        if not ease_variable:
            print("Easing Initiated")
            for i in range(WIDTH):
                for j in range(WIDTH):
                    a = QuadEaseInOut(start=DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)], end= 0, duration= 15)

                    y0 = list(map(a.ease, ease_range))
                    y0.reverse()
                    # y0.extend(reversed(y0))
                    # print(y0)
                    
                    FadeBox[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)] =  y0
            
            FrameIndex = len(ease_range) - 1
            
            ease_variable = True
            
        if not (sign + 1):
            # print("Easing in Process")
            for i in range(WIDTH):
                for j in range(WIDTH):
                    DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)] =  FadeBox[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)][FrameIndex]
            
            FrameIndex += 1 * sign

            if FrameIndex == 0:
                sign = 1
        else:
            for i in range(WIDTH):
                for j in range(WIDTH):
                    DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)] =  FadeBox[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)][FrameIndex]

            FrameIndex += 1 * sign
            if FrameIndex == len(ease_range) - 1:

                sign = -1
    
    #Snake movement Generation: when the toggle is on, the position coordinates for the snake are generated based on bezier curves stitching. 
    if SNEK_TOGGLE:
        snake_length = 3
        st = frameCount % (len(s_tracker) - snake_length)
        
        if st == 0:
            s_tracker = []
            snake(WIDTH / 3)
            
        else:
            for i in range(snake_length):
                x = int(s_tracker[st + i][0])
                y = int(s_tracker[st + i][1])

                bright = 1
                DENS[FLUID.xy_coordinate(WIDTH, x + 1, y + 1)] += bright
                
            # for i in range(0, snake_length):
            #     x = int(s_tracker[st - i][0])
            #     y = int(s_tracker[st - i][1])
                
            #     bright = 0.7
            #     DENS[FLUID.xy_coordinate(WIDTH, x + 1, y + 1)] -= bright / (snake_length + 1 - i)
  
    #AMOEBA movements generation
    if AMOEBA_TOGGLE:
        directionX += randint(-4,4) * 4
        directionY -= randint(-1,1)
        calcWave()
        renderWave()
        generate_amoeba()
    
    if TEST_TOGGLE:
        if frameCount % 2 == 0:
            print("Index %d On" % testIndex)
            DENS[testIndex - 1] = 0
            DENS[testIndex] = 1
            testIndex+=1
    
    if(frameCount % 100 == 0):
        VEL_H, VEL_V, VEL_HPREV, VEL_VPREV = FLUID.velocity_step(WIDTH, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, VISCOSITY, TIME_SPACE)
    
        if AMOEBA_TOGGLE:
            for i in location_tracker[:200]:
                center_x = i[0]
                center_y = i[1]
                
                bright = 1
                center_x = 4
                center_y = 4
                DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] += bright
                DENS[FLUID.xy_coordinate(WIDTH, center_x, center_y + 1)] += bright
                # DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y)] += bright
                # DENS[FLUID.xy_coordinate(WIDTH, center_x + 2, center_y + 1)] += bright
                # DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 2)] += bright
            
            location_tracker = []
        
    DENS, DENS_PREV = FLUID.density_step(WIDTH, DENS, DENS_PREV, VEL_H, VEL_V, D_RATE, TIME_SPACE) 
    
    if frameCount % 7 == 0 :
        for i in xrange(WIDTH):
            for j in xrange(WIDTH):
                DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)] -= 0.01
            
    reset_gridcells()
    display_grid()
    
    #Write to Arduino
    if MAGNET_CONNECTION:
        if not INITIALIZED:
            initialize_port()
        
        pos = 537
        carr = count()
        # print(carr[pos])
        reordered_list = reordinator(carr)
        
        # byte message to send
        byteMessage = ''
        # for idx, i in enumerate(carr):
        
        x = 1
        if rampsign:
            j = (frameCount % (127 * x) / float(x))
        else:
            j = abs(126 - (frameCount % (127 * x) / float(x)))
            
        if j == 126:
            rampsign = False
        elif j == 0:
            rampsign = True
        else:
            pass
        # print(j, len(reordered_list))
            
        for idx, i in enumerate(reordered_list):
            i = j
            try:
                byteMessage+=chr(int(round(i)))
            except:
                print("BAD NUMBER", i, idx)
                byteMessage+=chr(int(round(0.0)))
        
        # thread logic
        if sendThread.isAlive():
            busyCount += 1
            openCount = 0
            print("Thread BUSY", busyCount)
            pass
        else:
            # print("regular")
            sendThread = Thread(target = threadSerial, args = [byteMessage])
            sendThread.start()
            busyCount = 0
            openCount += 1
            print("OPEN Thread", openCount)
            # print("Thread GOOD!", busyCount)

def keyPressed():
    global ON_TOGGLE, TEST_TOGGLE, EASING_TOGGLE, DENS, DENS_PREV, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, BUBBLE_TOGGLE, SNEK_TOGGLE, D_RATE, AMOEBA_TOGGLE, MAGNET_CONNECTION
    
    if ((key == 'R') or (key == 'r')):
        DENS = [0 for _ in xrange(SIZE)]
        DENS_PREV = [0 for _ in xrange(SIZE)]
        VEL_H = [0 for _ in xrange(SIZE)]
        VEL_HPREV = [0 for _ in xrange(SIZE)]
        VEL_V = [0 for _ in xrange(SIZE)]
        VEL_VPREV = [0 for _ in xrange(SIZE)]
        
    if ((key == 'F') or (key == 'f')):
        D_RATE = 0.05
        center_x = mouseX // sf
        center_y = mouseY // sf
        
        bval = 1
        
        pos = FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1) 
        print(pos)
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 2, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 2)] += bval
          
    if ((key == 'S') or (key == 's')):
        D_RATE = 0.05
        SNEK_TOGGLE = not SNEK_TOGGLE
        
        if SNEK_TOGGLE:
            print("SNAKE ON")
        else:
            print("SNAKE OFF")
    
    if ((key == 'C') or (key == 'c')):
        MAGNET_CONNECTION = not MAGNET_CONNECTION
        
        if MAGNET_CONNECTION:
            print("MAGNET CONNECTION ON")
        else:
            print("MAGNET CONNECTION OFF")
        
    if ((key == 'A') or (key == 'a')):
        D_RATE = 0.05
        AMOEBA_TOGGLE = not AMOEBA_TOGGLE
        if AMOEBA_TOGGLE:
            print("AMOEBA ON")
        else:
            print("AMOEBA OFF")
    
    if ((key == 'E') or (key == 'e')):
        EASING_TOGGLE = not EASING_TOGGLE
        if EASING_TOGGLE:
            print("EASING ON")
        else:
            print("EASING OFF")
        
    if ((key == 'M') or (key == 'm')):
        center_x = mouseX // sf
        center_y = mouseY // sf

        for i in easelist():
            DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = i
    
    if ((key == 'T') or (key == 't')):
        TEST_TOGGLE = not TEST_TOGGLE
        D_RATE = 0.0
        
        if TEST_TOGGLE:
            print("TESTING ON")
        else:
            DENS = [0 for _ in xrange(SIZE)]
            print("TESTING OFF")
            
    if ((key == 'O') or (key == 'o')):
        ON_TOGGLE = not ON_TOGGLE
        D_RATE = 0.0
        
        if ON_TOGGLE:
            DENS = [1 for _ in xrange(SIZE)]
            print("ALL MAGNETS ON")
        else:
            DENS = [0 for _ in xrange(SIZE)]
            print("ALL MAGNETS OFF")
            
    if ((key == 'Q') or (key == 'q')):
        title = str(time())
        saveFrame(title + ".png");
        val_mat = createWriter(title + ".txt")
        
        for j in xrange(WIDTH):
            for i in xrange(WIDTH):
                val_mat.print("%.2f " % DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)])
            val_mat.print("\n")
        
        val_mat.close()

def ratio(x):
    r = x * 127
    if r > 127:
        return 127
    elif r < 0:
        return 0
    else:
        return r
    
def count():
    global DENS, WIDTH, FLUID
    counter = []

    for j in range(WIDTH):
        for i in range(WIDTH):
            counter.append(ratio(DENS[FLUID.xy_coordinate(WIDTH, i + 1, j + 1)]))
    
    return counter

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
                GRID[i][j].display()

class Cell():
    def __init__(self, tempX, tempY, tempW, tempH, tempDens):
        self.x = tempX
        self.y = tempY
        self.w = tempW
        self.h = tempH
        self.tempDens = tempDens
        self.Max = 0
        
    def display(self):
        noStroke()
        fill(0, self.tempDens * 255, 0)
        rect(self.x,self.y,self.w,self.h)
        
def calcWave():
    global theta, directionxSWITCH
        
    theta += 0.5
    
    # For every x varlue, calculate a y value with sine function
    x = theta
    for i in range(len(yvalues)):
        yvalues[i] = sin(x) * amplitude
        x += dx

def renderWave():
    global counter, angle, sf, location_tracker, randposX, randposY
    noStroke()
    fill(255)
        
    for x in range(len(yvalues)):
        val_x = x * xspacing + directionX
        val_y = (height/2 + yvalues[x]) + directionY
        
        val_x = ((val_x) * (cos(angle)) - (val_y) * (sin(angle))) // sf
        val_y = ((val_x) * (sin(angle)) + (val_y) * (cos(angle))) // sf

        location_tracker.append((val_x, val_y))
        
def generate_amoeba():
    global angle, period, xspacing
    angle -= ((TWO_PI / period) * xspacing)*25

#Port Initialization
def initialize_port():
    global INITIALIZED, magnetPort
    print(Serial.list())
    arduinoPort = Serial.list()[3]
    magnetPort = Serial(this, arduinoPort, 1000000)
    
    INITIALIZED = True

def snake(w):
    global nax, nay, fcx, fcy, scx, scy, nax1, nay1, s_tracker
    
    m = (float(nay) - fcy) / (float(nax) - fcx)
    b = nay - (m * nax)
    scx = nax - (fcx - nax)
    scy = m * scx + b
    
    fcx = randint(0, w) 
    fcy = randint(0, w)
    nax1 = genrandi(w, fcx)
    nay1 = genrandi(w, fcy)
    
    steps = 400
    # print(steps)
    
    for i in range(0, steps):
        t = i / float(steps)
        x = bezierPoint(nax, scx, fcx, nax1, t)
        y = bezierPoint(nay, scy, fcy, nay1, t)
        
        s_tracker.append((x, y))
        
    nax = nax1
    nay = nay1
