add_library('serial')
add_library('opencv_processing')

import fluid as Fluid
import magnet_map as MagnetMap
import tests as Tests
from random import randint 
from time import sleep, time
import math
#import struct
#from threading import Thread
#import struct

'''
KEYBOARD CONTROLS:
    s: toggle snek mode
    m: toggle morph mode
    t: toggle test sequence (if snek or morph is active, toggle that off before using this)
    b: toggle bloom mode
    o: all magnets on
    r: reset all to 0
    f: activate area around mouse pointer
    d: activate single magnet under mouse pointer
'''

DEBUG_MODE = False # when true, program only runs magnet test sequence. Same test as 't' key
NO_SERIAL_MODE = False

WINDOW_WIDTH = 720 # ** width and height
WINDOW_HEIGHT = int(720 * 46/40)

#GLOBAL VARIABLES FOR NAVIER_STOKES
WIDTH = 40
HEIGHT = 46 # ** NEW V2.0
D_RATE = 0.1
VISCOSITY = 0.2
TIME_SPACE = 0.001

#GLOBAL VARIABLES FOR Bloom_NAVIER_STOKES
BLOOM_D_RATE = 0.001
BLOOM_VISCOSITY = 0.1
BLOOM_TIME_SPACE = 0.05

#GLOBAL GRID 
GRID =[]
FLUID = Fluid.fluid(WIDTH, HEIGHT, D_RATE, VISCOSITY, TIME_SPACE) 

#Velocity and Density Fields
SIZE = (WIDTH+2)*(HEIGHT+2)
VEL_HPREV = [0] * SIZE
VEL_H = [0 for _ in xrange(SIZE)]
VEL_VPREV = [0] * SIZE
VEL_V = [0 for _ in xrange(SIZE)]
DENS = [0 for _ in xrange(SIZE)]
DENS_PREV = [0] * SIZE


#Serial Connection
serialPortAddresses = ['/dev/cu.usbmodem112386001', # top left
                       '/dev/cu.usbmodem51843401',  # top right
                       '/dev/cu.usbmodem112386301', # bottom left
                       '/dev/cu.usbmodem112386201'] # bottom right

serialPorts = []
INITIALIZED = False

sf = 1 # cell size

#TOGGLES
SNEK_TOGGLE = True
TEST_TOGGLE = False
ON_TOGGLE = False
MORPH_TOGGLE = False
BLACK_OUT = False
BLOOM_TOGGLE = False

if DEBUG_MODE:
    SNEK_TOGGLE = False
    TEST_TOGGLE = True

testStep =  -1
#testStep = 22 * (WIDTH)

def genrandi(maxn, num):
    newi = randint(0, maxn)
    while(newi == num):
        newi = randint(0, maxn)
    return newi

#Snake Globals
fcx = randint(0, WIDTH)
fcy = randint(0, HEIGHT)
nax = genrandi(WIDTH, fcx)
nay = genrandi(HEIGHT, fcy)
scx = randint(0, WIDTH)
scy = randint(0, HEIGHT)
nax1 = randint(0, WIDTH)
nay1 = randint(0, HEIGHT)

s_tracker = []

#Morphing
render = []
shape0 = []
shape1 = []

morph_refresh = True

pset_0 = None
cset_0 = None
pset_1 = None
cset_1 = None

img_idx = 0
rand_lt = [0.003, 0.008]
randspeed = 0.001
lastDistance = 0

#Timer globals
snake_interval_min = 2500
snake_interval_max = 3250
blackout_interval_min = 250
blackout_interval_max = 350
morph_interval_min = 1500
morph_interval_max = 2250
bloom_interval_min = 500
bloom_interval_max = 600
bloom_counter = 0
bloom_frequency = 2 # number of full loops before bloom appears
timer = randint(snake_interval_min, snake_interval_max)
multiplier = 1.0
mode_idx = 0

FRAME_BUFFER = None # ** image object, to write pixels from GRID

def settings():
    size(WINDOW_WIDTH, WINDOW_HEIGHT) # window size
    smooth(2)

def setup():
    global GRID, WIDTH, HEIGHT, sf, w, yvalues, FRAME_BUFFER

    background(0)

    #Initializing the Navier Stokes grid.
    GRID = makeGrid(WIDTH, HEIGHT) # ** Grid of Cells

    FRAME_BUFFER = createGraphics(WIDTH + 2, HEIGHT + 2) # ** offscreen renderer

    #Generating coordinates for snake movements.
    snake(WIDTH, HEIGHT)
    frameRate(25)
    strokeWeight(0)


    initialize_port()


def draw():
    global lastDistance, multiplier, mode_idx, BLACK_OUT, timer, \
        MORPH_TOGGLE, rand_lt, randspeed, img_idx, morph_refresh, src, render, shape0, shape1, pset_0, cset_0, pset_1, pset_1, src_cv, det_cv,\
        TEST_TOGGLE, s_tracker, INITIALIZED, randposX, randposY, \
        GRID, WIDTH, HEIGHT, D_RATE, VISCOSITY, TIME_SPACE, \
        BLOOM_D_RATE, BLOOM_VISCOSITY, BLOOM_TIME_SPACE, \
        VEL_H, VEL_HPREV, VEL_V, VEL_VPREV, \
        DENS, DENS_PREV, SNEK_TOGGLE, sf, FRAME_BUFFER, testStep, \
        snake_interval_min, snake_interval_max, blackout_interval_min, blackout_interval_max, morph_interval_min, morph_interval_max, \
        bloom_interval_min, bloom_interval_max, bloom_counter, bloom_frequency, BLOOM_TOGGLE
    
    background(0)
    
    # ** timer is used to switch between SNEK and MORPH modes by flipping SNEK_TOGGLE and MORPH_TOGGLE.
    # ** SNEK mode is a moving peak that follows generative bezier curves. Only mode where navier-stokes is used.
    # ** MORPH mode interpolates between shapes saved in the image files in data/

    # ** progresses through modes 0,1,2 in order spending random amount of time on each
    if timer <= 0 and not TEST_TOGGLE:
        if timer <= 0:
            mode_idx = (mode_idx + 1) % 6
            
        if mode_idx == 0:
            SNEK_TOGGLE = True
            BLACK_OUT = False
            timer += randint(snake_interval_min, snake_interval_max)
            
        elif mode_idx == 1:
            BLACK_OUT = True
            SNEK_TOGGLE = False
            timer += randint(blackout_interval_min, blackout_interval_max)
                             
        elif mode_idx == 2:
            morph_refresh = True
            MORPH_TOGGLE = True
            BLACK_OUT = False
            timer += randint(morph_interval_min, morph_interval_max)    
        
        elif mode_idx == 3:
            BLACK_OUT = True
            MORPH_TOGGLE = False
            timer += randint(blackout_interval_min, blackout_interval_max)
            
        elif mode_idx == 4:
            if bloom_counter == bloom_frequency - 1:
                BLACK_OUT = False
                BLOOM_TOGGLE = True
                timer += randint(bloom_interval_min, bloom_interval_max)
            print("BLOOM", bloom_counter)
            
        else:
            BLACK_OUT = True
            BLOOM_TOGGLE = False
            
            if bloom_counter == bloom_frequency - 1:
                timer += randint(blackout_interval_min, blackout_interval_max)
            bloom_counter = (bloom_counter + 1) % (bloom_frequency)
            print("Post increment", bloom_counter)
    
    timer -= 1 
    
    if not TEST_TOGGLE:
        if not BLOOM_TOGGLE:
            if timer > 100:
                multiplier += 0.01
            elif timer <= 100:
                multiplier = 0.01 * timer
        else:
            if timer > 10:
                multiplier += 0.01
            else:
                multiplier = 0.0
                    
        if multiplier > 1.0:
            multiplier = 1.0
        elif multiplier < 0.0:
            multiplier = 0.0
    
    # print("Timer: %d, SNEK: %d, MORPH: %d, BLACK: %d " % (timer, SNEK_TOGGLE, MORPH_TOGGLE, BLACK_OUT))
        
    if MORPH_TOGGLE:
        totalDistance = 0
        
        if morph_refresh: # ** set new start and target shapes
            set_morphing()
            randspeed = rand_lt[randint(0, len(rand_lt) - 1)]
    
        # ** each vertex in the current shape
        for i in range(len(render)):
            v1 = shape1[i]
            render = shape0
            
            # Get the vertex we will draw.
            v2 = render[i]
            
            # Lerp to the target
            v2.lerp(v1, randspeed)
    
            # Check how far we are from target.
            totalDistance += PVector.dist(v1, v2)
    
        # # If all the vertices are close, switch shape.
        distance_change = lastDistance - totalDistance
        
        if (distance_change < 4 and distance_change > 0):
            morph_refresh = True
            lastDistance = 0 
        
        lastDistance = totalDistance
        
        FRAME_BUFFER.beginDraw()
        FRAME_BUFFER.fill(255)
        # Draw a polygon that makes up all the vertices
        FRAME_BUFFER.beginShape()
        for vector in render:
            FRAME_BUFFER.vertex(vector.x, vector.y)
        FRAME_BUFFER.endShape()
        FRAME_BUFFER.filter(BLUR, 1)
        FRAME_BUFFER.endDraw()
        
        FRAME_BUFFER.loadPixels()
        
        for i in range(len(FRAME_BUFFER.pixels)):
            DENS[i] = (FRAME_BUFFER.pixels[i] & 255) / float(255)
        
    #Snake movement Generation: when the toggle is on, the position coordinates for the snake are generated based on bezier curves stitching. 
    if SNEK_TOGGLE or BLOOM_TOGGLE:
        translate(1, 1)
        snake_length = 3
        st = frameCount % (len(s_tracker) - snake_length)
        
        if st == 0:
            s_tracker = []
            snake(WIDTH, HEIGHT)
            
        else:
            for i in range(snake_length):
                x = int(s_tracker[st + i][0])
                y = int(s_tracker[st + i][1])

                bright = floor(1 * multiplier)
                
                DENS[FLUID.xy_coordinate(WIDTH, x + 1, y + 1)] += bright

    if TEST_TOGGLE:
        if frameCount % 2 == 0:
            testStep = (testStep + 1) % (WIDTH * HEIGHT)
            Tests.test_sequence(testStep, WIDTH, HEIGHT, DENS, FLUID)
            #print(testStep)
    
    if SNEK_TOGGLE: # ** navier-stokes is only used in SNEK mode
        DENS, DENS_PREV = FLUID.density_step(WIDTH, HEIGHT, DENS, DENS_PREV, VEL_H, VEL_V, D_RATE, TIME_SPACE) 
         
    if BLOOM_TOGGLE:
        DENS, DENS_PREV = FLUID.density_step(WIDTH, HEIGHT, DENS, DENS_PREV, VEL_H, VEL_V, BLOOM_D_RATE, BLOOM_TIME_SPACE) 

    # ** update cells in grid using multiplier based on timer. Without this loop, green never fades to black in SNEK mode
    for i in xrange(HEIGHT):
        for j in xrange(WIDTH):
            DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] -= 0.004
            DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] = DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] * multiplier
    

    reset_gridcells()
    display_grid()
    
    image(FRAME_BUFFER, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    #Write to Arduino
    
    if INITIALIZED:
        send_to_parsers()


        
def keyPressed():
    global testIndex, testStep, MORPH_TOGGLE, ON_TOGGLE, TEST_TOGGLE, \
        DENS, DENS_PREV, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, SNEK_TOGGLE, D_RATE, \
        BLOOM_TOGGLE, BLOOM_D_RATE
    
    if ((key == 'R') or (key == 'r')): # ** set all to 0
        DENS = [0 for _ in xrange(SIZE)]
        DENS_PREV = [0 for _ in xrange(SIZE)]
        VEL_H = [0 for _ in xrange(SIZE)]
        VEL_HPREV = [0 for _ in xrange(SIZE)]
        VEL_V = [0 for _ in xrange(SIZE)]
        VEL_VPREV = [0 for _ in xrange(SIZE)]
        
    if ((key == 'D') or (key == 'd')): # ** set pixel under mouse pointer to 100
        # map screen pixel to magnet coords
        center_x = int(float(mouseX) / WINDOW_WIDTH * WIDTH)
        center_y = int(float(mouseY) / WINDOW_HEIGHT * HEIGHT)
        
        print("MOUSE " + str(center_x) + ", " + str(center_y))
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = 100
        
    if ((key == 'F') or (key == 'f')): # ** set pixels to 100 in area around mouse pointer
        # map screen pixel to magnet coords
        center_x = int(float(mouseX) / WINDOW_WIDTH * WIDTH)
        center_y = int(float(mouseY) / WINDOW_HEIGHT * HEIGHT)
        
        print("MOUSE " + str(center_x) + ", " + str(center_y))
        
        bval = 100
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 2, center_y + 1)] += bval
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 2)] += bval
          
    if ((key == 'S') or (key == 's')):
        D_RATE = 0.1
        SNEK_TOGGLE = not SNEK_TOGGLE
        
        if SNEK_TOGGLE:
            print("SNAKE ON")
        else:
            print("SNAKE OFF")
    
    if ((key == 'M') or (key == 'm')):
        MORPH_TOGGLE = not MORPH_TOGGLE
        
        if MORPH_TOGGLE:
            print("MORPH ON")
        else:
            print("MORPH OFF")
            
    if ((key == 'T') or (key == 't')):
        TEST_TOGGLE = not TEST_TOGGLE
        testStep = -1
        D_RATE = 0.0
        
        if TEST_TOGGLE:
            print("TESTING ON")
        else:
            DENS = [0 for _ in xrange(SIZE)]
            print("TESTING OFF")
            
    if ((key == 'B') or (key == 'b')):
        D_RATE = BLOOM_D_RATE
        BLOOM_TOGGLE = not BLOOM_TOGGLE
        
        if BLOOM_TOGGLE:
            print("BLOOM ON")
        else:
            print("BLOOM OFF")
            
    if ((key == 'O') or (key == 'o')):
        ON_TOGGLE = not ON_TOGGLE
        D_RATE = 0.0
        
        if ON_TOGGLE:
            DENS = [1 for _ in xrange(SIZE)]
            print("ALL MAGNETS ON")
        else:
            DENS = [0 for _ in xrange(SIZE)]
            print("ALL MAGNETS OFF")
            

def stop():
    close_ports()
    print("exiting")
    

def ratio(x): # convert float to int within [0, 127]
    # return (x / 2)
    if(x < 0):
        return 0
    elif (x * 127) > 127:
        return 127
    else:
        return int(x * 127)
    
def count(): # ** make list of converted density values to send to arduino
    global DENS, WIDTH, HEIGHT, FLUID, BLOOM_FLUID
    counter = []
    
    # current counter - goes left to right, then top to bottom
    for i in range(HEIGHT+2):
        for j in range(WIDTH+2):
            counter.append(ratio(DENS[FLUID.xy_coordinate(WIDTH, j, i)]))


    return counter

def send_to_parsers():
    global WIDTH, HEIGHT, magnetPorts
    
    n_parsers = len(serialPorts)
    
    carr = count() # ** convert values for sending
    
    x_index = 0
    y_index = 0
    
    for n in range(n_parsers):
        if n == 2:
            y_index += 1
            x_index = 0
        mapped = MagnetMap.map_parser(x_index, y_index, WIDTH + 2, HEIGHT + 2, carr)
        sendSerial(mapped, n)
        x_index += 1

def sendSerial(infosend, port):
    global serialPorts

    #print("SENDING")

    if infosend != None and port < len(serialPorts):

        try:
            for i in range(len(infosend)):
                serialPorts[port].write(infosend[i])            
        except Exception as err:
            print("[!!!] Exception in sendSerial. Port = " + str(port))
            print(err)


def reset_gridcells():
    global DENS, WIDTH, HEIGHT, GRID
    for i in xrange(HEIGHT):
        for j in xrange(WIDTH):
            GRID[i][j] = Cell(j*sf,i*sf,sf, sf, DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)]) # ** IMPROVEMENT: this is creating a new Cell instance for each pixel, each frame
    
def makeGrid(wth,hgt):
    global GRID 
    for i in xrange(hgt):
        # Create an empty list for each row
        GRID.append([])
        for j in xrange(wth):
            # Pad each column in each row with a 0
            GRID[i].append(0)
            
    return GRID

def display_grid():
    global GRID, WIDTH, HEIGHT, FRAME_BUFFER

    FRAME_BUFFER.beginDraw()
    FRAME_BUFFER.background(0)

    FRAME_BUFFER.noStroke()
    for i in xrange(HEIGHT):
        for j in xrange(WIDTH):
            if GRID[i][j].tempDens:
                GRID[i][j].display(FRAME_BUFFER)

    FRAME_BUFFER.endDraw()
    

class Cell(): # ** an element in the grid / a pixel
    def __init__(self, tempX, tempY, tempW, tempH, tempDens):
        self.x = tempX
        self.y = tempY
        self.w = tempW
        self.h = tempH
        self.tempDens = tempDens
        
    def display(self, fb):
        fb.fill(0, self.tempDens * 255, 0)
        fb.rect(self.x+1, self.y+1, self.w, self.h)

#Port Initialization
def initialize_port():
    global INITIALIZED, serialPortAddresses, serialPorts

    try:
        print("INITIALIZING")
        if not NO_SERIAL_MODE:
            for each in serialPortAddresses:
                serialPort = Serial(this, each, 1000000)
                serialPorts.append(serialPort)
        
        INITIALIZED = True
        print("ARDUINO SERIAL INITIALIZED")
    except Exception as err:
        print("[!!!] Exception in initialize_port")
        print(err)
        
def close_ports():
    # ** https://www.processing.org/reference/libraries/serial/Serial_stop_.html
    global INITIALIZED, serialPorts

    if INITIALIZED:
        try:
            print("CLOSING PORTS")
            for p in serialPorts:
                p.clear()
                p.stop()
        except Exception as err:
            print("[!!!] EXCEPTION in close_ports")
            print(err)
    
    
def snake(w, h):
    global nax, nay, fcx, fcy, scx, scy, nax1, nay1, s_tracker
    
    m = (float(nay) - fcy) / (float(nax) - fcx)
    b = nay - (m * nax)
    scx = nax - (fcx - nax)
    scy = m * scx + b
    
    fcx = randint(0, w) 
    fcy = randint(0, h)
    nax1 = genrandi(w, fcx)
    nay1 = genrandi(h, fcy)
    
    steps = 140 #185
    
    for i in range(0, steps):
        t = i / float(steps)
        x = bezierPoint(nax, scx, fcx, nax1, t)
        y = bezierPoint(nay, scy, fcy, nay1, t)
        
        s_tracker.append((x, y))
        
    nax = nax1
    nay = nay1
    
def linspace(a, b, n=100):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a  for i in range(n)]

def set_morphing():
    # ** called in draw when MORPH mode is active.
    # ** chooses two random images from data/, uses opencv to find polygons in each
    # ** One is start shape, other is target
    # ** then in draw, vertices in start are lerped to target until they are close enough
    # ** which triggers another call to set_morphing.

    global img_idx, morph_refresh, render, shape0, shape1, pset_0, cset_0, pset_1, pset_1, src_cv, det_cv
    
    render = []
    shape0 = []
    shape1 = []
    
    new_idx = randint(0, 999)

    # ** this function is called during draw(), so loading these files is probably causing the lag when a new shape is chosen
    src = loadImage("s" + str(img_idx) + ".png")
    det = loadImage("s" + str(new_idx) + ".png")
    
    src_cv = OpenCV(this, src)
    det_cv = OpenCV(this, det)
    
    tnum = 40
    src_cv.threshold(tnum)
    det_cv.threshold(tnum)

    clist = [len(c.getPoints()) for c in src_cv.findContours()]
    clist1 = [len(c.getPoints()) for c in det_cv.findContours()]
    
    mi = clist.index(max(clist))
    mi1 = clist1.index(max(clist1))
    
    pset_0 = src_cv.findContours()[mi].getPoints()
    cset_0 = src_cv.findContours()[mi]
    
    pset_1 = det_cv.findContours()[mi1].getPoints()
    cset_1 = det_cv.findContours()[mi1]
    
    lt1 = linspace(0, len(pset_0) - 1, 200)
    lt2 = linspace(0, len(pset_1) - 1, 200)
    
    for i in lt1:
        shape0.append(pset_0[int(i)])

    for i in lt2:
        shape1.append(pset_1[int(i)])
        
        render.append(pset_1[int(i)])
    
    # g.removeCache(src)
    # g.removeCache(det)
    morph_refresh = False
    img_idx = new_idx
