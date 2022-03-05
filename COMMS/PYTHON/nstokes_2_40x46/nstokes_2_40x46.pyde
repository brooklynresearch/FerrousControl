add_library('serial')
add_library('opencv_processing')

import fluid as Fluid
import magnet_map as MagnetMap
import tests as Tests
from random import randint 
from time import sleep, time
import math
import struct
from threading import Thread
import struct

TILE_1 = False
LETTER_MODE = False # TESTING: Send ASCII 'A' for all values

#GLOBAL VARIABLES FOR NAVIER_STOKES
WIDTH = 40
HEIGHT = 46 # ** NEW V2.0
D_RATE = 0.2
VISCOSITY = 0.8
TIME_SPACE = 0.0001

#GLOBAL GRID 
GRID =[]
FLUID = Fluid.fluid(WIDTH, HEIGHT, D_RATE, VISCOSITY, TIME_SPACE) 

#Velocity and Density Fields
SIZE = (WIDTH+2)*(HEIGHT+2) # ** NEW V2.0
VEL_HPREV = [0] * SIZE
VEL_H = [0 for _ in xrange(SIZE)]
VEL_VPREV = [0] * SIZE
VEL_V = [0 for _ in xrange(SIZE)]
DENS = [0 for _ in xrange(SIZE)]
DENS_PREV = [0] * SIZE

#Serial Connection
magnetPort = None
magnetPort2 = None

# ** Need to change these for linux
# Mac Mini
#magnetPortAddresses = [
#               u'/dev/cu.usbmodem5804040',
#               u'/dev/cu.usbmodem4927000',
#               u'/dev/cu.usbmodem5813060',
#               u'/dev/cu.usbmodem4331810',
#               u'/dev/cu.usbmodem4331800']

# ** Linux version
# magnetPortAddresses = [u'/dev/ttyACM0']

# Version 2.0
magnetPortAddresses = ['/dev/cu.usbmodem112386001']

magnetPorts = []
INITIALIZED = False
MAGNET_CONNECTION = False

STARTING = 0
sf = 1

#TOGGLES
SNEK_TOGGLE = False
TEST_TOGGLE = False
ON_TOGGLE = False
MORPH_TOGGLE = False
BLACK_OUT = False
testIndex = WIDTH + 2
testStep = -1 # ** mine

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

state = False
morph_refresh = True

pset_0 = None
cset_0 = None
pset_1 = None
cset_1 = None

img_idx = 0
rand_lt = [0.003, 0.008]
randspeed = 0.001
lastDistance = 0

FRAME_BUFFER = None # ** image object, to write pixels from GRID

def sendSerial(infosend, port):
    global magnetPorts

    #print("SENDING")

    if infosend != None and port < len(magnetPorts):

        try:
            # as byte message
            # msg = byteConverter(infosend)
            # magnetPorts[port].write(msg)
            #magnetPorts[port].write(255)
            for i in range(len(infosend)):
                magnetPorts[port].write(infosend[i])
                # magnetPorts[port].write(i % 40)
                
        except:
            # print("error in send", port)
            pass

'''
def byteConverter(inlist):
    byteMessage = ''
    for idx, i in enumerate(inlist):
        try:
            val = 127 if idx < 24 else 0
            # val = i
            byteMessage+=chr(int(round(val)))
        except:
            print("BAD NUMBER", i, idx)
            byteMessage+=chr(int(round(0.0)))
            
    return byteMessage
'''

# Send
busyCount = 0
openCount = 0
startTime = time()
startFrame = 0

WINDOW_WIDTH = 720 # ** width and height
WINDOW_HEIGHT = int(720 * 46/40)

'''
# ** IMPROVEMENT: whatever this is doing, this is not the way to do it
def reordinator(initial_list): # ** done every frame before sending to arduino. Because magnet array is larger than GRID?
    reordered_list = []
    
    # ** looks worse than it is. 1600 steps, same as iterating through GRID
    for panel_y in range(5):
        for panel_x in range(5):
            for quad_y in range(2):
                for quad_x in range(2):
                    for mag_y in  range(4):
                        for mag_x in range(4):
                            index = mag_x + mag_y * 40 + quad_x * 4 + quad_y * 160 + panel_x * 8 + panel_y * 320
                            reordered_list.append(initial_list[index])
                            
    return reordered_list
    # return initial_list
'''

def setup():
    # ** IMPROVEMENT: decouple display window from the calculations by creating an image object with 42 x 42 pixels
    # ** which gets drawn to the canvas every update. change display_grid and the MORPH mode section in update
    # ** to write to the image pixels instead of the window. https://py.processing.org/reference/createImage.html
        
    global FLUID, GRID, WIDTH, HEIGHT, D_RATE, VISCOSITY, TIME_SPACE, sf, w, yvalues, FRAME_BUFFER
    background(0)
    size(WINDOW_WIDTH, WINDOW_HEIGHT, P2D) # window size

    #Initializing the Navier Stokes grid.
    GRID = makeGrid(WIDTH, HEIGHT) # ** Grid of Cells

    FRAME_BUFFER = createGraphics(WIDTH + 2, HEIGHT + 2, P2D) # ** offscreen renderer

    #Generating coordinates for snake movements.
    snake(WIDTH, HEIGHT)
    frameRate(25)
    strokeWeight(0)
    smooth(2)

    initialize_port()

ramp_up = True
power = 0

timer = randint(4500, 5250)
state = 0
multiplier = 1.0
mode_idx = 0

def draw():
    global lastDistance, multiplier, mode_idx, BLACK_OUT, state, timer, MORPH_TOGGLE, rand_lt, randspeed, img_idx, morph_refresh, src, state, render, shape0, shape1, pset_0, cset_0, pset_1, pset_1, src_cv, det_cv,\
        ramp_up, power, testIndex, TEST_TOGGLE, s_tracker, MAGNET_CONNECTION, INITIALIZED, magnetPort, randposX, randposY, GRID, WIDTH, HEIGHT, D_RATE, VISCOSITY, TIME_SPACE, VEL_H, VEL_HPREV, VEL_V, VEL_VPREV, \
        DENS, DENS_PREV, STARTING, BUBBLE_TOGGLE, SNEK_TOGGLE, AMOEBA_TOGGLE, sf, sendThread, busyCount, openCount, startTime, startFrame, FRAME_BUFFER, TILE_1, testStep
    background(0)

    
    # ** timer is used to switch between SNEK and MORPH modes by flipping SNEK_TOGGLE and MORPH_TOGGLE.
    # ** SNEK mode is a moving peak that follows generative bezier curves. Only mode where navier-stokes is used.
    # ** MORPH mode interpolates between shapes saved in the image files in data/

    # ** progresses through modes 0,1,2 in order spending random amount of time on each
    if timer <= 0 and not TEST_TOGGLE:
        if timer <= 0:
            mode_idx = (mode_idx + 1) % 4
            
        if mode_idx == 0:
            SNEK_TOGGLE = True
            BLACK_OUT = False
            timer += randint(4500, 5250)
            
        elif mode_idx == 1:
            BLACK_OUT = True
            SNEK_TOGGLE = False
            timer += randint(250, 375)
                             
        elif mode_idx == 2:
            morph_refresh = True
            MORPH_TOGGLE = True
            BLACK_OUT = False
            timer += randint(1500, 2250)
            
        else:
            BLACK_OUT = True
            MORPH_TOGGLE = False
            timer += randint(250, 375)
    
    timer -= 1 
    
    if not TEST_TOGGLE:
        if timer > 100:
            multiplier += 0.01
        elif timer <= 100:
            multiplier = 0.01 * timer
        
        if multiplier > 1.0:
            multiplier = 1.0
        elif multiplier < 0.0:
            multiplier = 0.0
    
    # print("Timer: %d, SNEK: %d, MORPH: %d, BLACK: %d " % (timer, SNEK_TOGGLE, MORPH_TOGGLE, BLACK_OUT))
        
    if MORPH_TOGGLE:
        #FRAME_BUFFER.translate(1, 1)
        totalDistance = 0
        
        if morph_refresh: # ** set new start and target shapes
            set_morphing()
            randspeed = rand_lt[randint(0, len(rand_lt) - 1)]
    
        # ** each vertex in the current shape
        for i in range(len(render)):
            if state:
                v1 = shape0[i]
                render = shape1
            else:
                v1 = shape1[i]
                render = shape0
            
            # Get the vertex we will draw.
            v2 = render[i]
            
            # Lerp to the target
            # print(v1, v2)
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
        # Draw a polygon that makes up all the vertices
        FRAME_BUFFER.beginShape()
        FRAME_BUFFER.fill(255)
        for vector in render:
            FRAME_BUFFER.vertex(vector.x, vector.y)
        FRAME_BUFFER.endShape()
        FRAME_BUFFER.filter(BLUR, 1)
        FRAME_BUFFER.endDraw()
        
        FRAME_BUFFER.loadPixels()
        
        # scene = [(p & 255) / float(255) for p in pixels]
        
        # if scene == DENS:
        #     morph_refresh = True
        #     lastDistance = 0 
        
        #DENS = [(p & 255) / float(255) for p in FRAME_BUFFER.pixels] # ** convert screen pixels into floats and load into density matrix.
        for i in range(len(FRAME_BUFFER.pixels)):
            DENS[i] = (FRAME_BUFFER.pixels[i] & 255) / float(255)
        
    #Snake movement Generation: when the toggle is on, the position coordinates for the snake are generated based on bezier curves stitching. 
    if SNEK_TOGGLE:
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
         
    # ** update cells in grid using multiplier based on timer. Without this loop, green never fades to black in SNEK mode
    for i in xrange(HEIGHT):
        for j in xrange(WIDTH):
            #pass
            DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] -= 0.004
            DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] = DENS[FLUID.xy_coordinate(WIDTH, j + 1, i + 1)] * multiplier
    

    if TILE_1:
        DENS = Tests.test_tile_map(0, 0, WIDTH+2, HEIGHT+2)
    
    # ** IMPROVEMENT: above loop and the next two function calls all iterate through DENS or GRID
    # ** which have the same dimensions so these should be combined
    reset_gridcells()
    display_grid()
    
    image(FRAME_BUFFER, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    xscale = 720 / 40
    yscale = WINDOW_HEIGHT / 46
    
    '''
    noFill()
    stroke(0, 0, 255)
    rect(0, 0, int(20 * xscale), int(20*yscale))
    stroke(255, 0, 0)
    rect(0, 0, int(4*xscale), int(4*yscale))
    '''



    #Write to Arduino
    
    if INITIALIZED: # IMPROVEMENT: combine the count() and reordinator() steps into single loop
        carr = count() # ** iterate through DENS, converting values for sending
        # reordered_list = reordinator(carr) # ** iterate through carr, which is converted values from DENS
        
        reordered = MagnetMap.map_parser(0, 0, WIDTH+2, HEIGHT+ 2, carr)
        #print("LEN(reordered): " + str(len(reordered)))

        

        #print("REORDERED[:24] " + str(reordered[:24]))
        sendSerial(reordered, 0)
        # sendSerial(reordered[600:640], 1)
        # sendSerial(reordered_list[640:960], 2)
        # sendSerial(reordered_list[960:1280], 3)
        # sendSerial(reordered_list[1280:1600], 4)
    
    # ** Number of times iterating through WIDTH x WIDTH arrays every draw()
    # ** SNEK mode: 11
    # **       6 in FLUID.density_step (5 in lin_solve, 1 in advect)
    # **       1 in line 303
    # **       1 in reset_gridcells()
    # **       1 in display_grid()
    # **       1 in count()
    # **       1 in reordinator()
    # ** MORPH mode: 6
    # **       1 in line 270
    # **       1 in line 303
    # **       1 in reset_gridcells()
    # **       1 in display_grid()
    # **       1 in count()
    # **       1 in reordinator()
    
def stop():
    # ** IMPROVEMENT: clear & close serial connections here
    # ** https://www.processing.org/reference/libraries/serial/Serial_stop_.html
    close_ports()
    print("exiting")
        
def keyPressed():
    global testIndex, testStep, MORPH_TOGGLE, ON_TOGGLE, TEST_TOGGLE, DENS, DENS_PREV, VEL_H, VEL_V, VEL_HPREV, VEL_VPREV, BUBBLE_TOGGLE, SNEK_TOGGLE, D_RATE, MAGNET_CONNECTION, LETTER_MODE
    
    if ((key == 'R') or (key == 'r')): # ** set all to 0
        DENS = [0 for _ in xrange(SIZE)]
        DENS_PREV = [0 for _ in xrange(SIZE)]
        VEL_H = [0 for _ in xrange(SIZE)]
        VEL_HPREV = [0 for _ in xrange(SIZE)]
        VEL_V = [0 for _ in xrange(SIZE)]
        VEL_VPREV = [0 for _ in xrange(SIZE)]
        
    if ((key == 'D') or (key == 'd')): # ** set pixel under mouse pointer to 100
        center_x = mouseX // sf
        center_y = mouseY // sf
        
        DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = 100
        
    if ((key == 'F') or (key == 'f')): # ** set pixels to 100 in area around mouse pointer
        center_x = mouseX // sf
        center_y = mouseY // sf
        
        bval = 100
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
    
    if ((key == 'M') or (key == 'm')):
        MORPH_TOGGLE = not MORPH_TOGGLE
        
        if MORPH_TOGGLE:
            print("MORPH ON")
        else:
            print("MORPH OFF")
    
    if ((key == 'N') or (key == 'n')):
        center_x = mouseX // sf
        center_y = mouseY // sf

        for i in easelist():
            DENS[FLUID.xy_coordinate(WIDTH, center_x + 1, center_y + 1)] = i
            
    if ((key == 'T') or (key == 't')):
        TEST_TOGGLE = not TEST_TOGGLE
        #testIndex = WIDTH + 1
        testStep = -1
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
    
    if ((key == 'A') or (key == 'a')):
        # COMMS TEST: send letter A
        # send_char('A', 600, 0)
        LETTER_MODE = not LETTER_MODE

def ratio(x): # convert float to int within [0, 127]
    # return (x / 2)
    if(x < 0):
        return 0
    elif (x * 127) > 127:
        return 127
    else:
        return int(x * 127)
    
def count(): # ** make list of converted density values to send to arduino. IMPROVEMENT: take array as arg instead of creating new one
    global DENS, WIDTH, HEIGHT, FLUID
    counter = []
    

    # current counter - goes left to right, then top to bottom
    for i in range(HEIGHT+2):
        for j in range(WIDTH+2):
            counter.append(ratio(DENS[FLUID.xy_coordinate(WIDTH, j, i)]))


    return counter

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

def display_grid(): # ** IMPROVEMENT: combine this with reset_gridcells to reduce number of iterations through GRID each frame
    global GRID, WIDTH, HEIGHT, FRAME_BUFFER

    FRAME_BUFFER.beginDraw()
    FRAME_BUFFER.background(0)

    #FRAME_BUFFER.fill(255, 255, 255)
    #FRAME_BUFFER.rect(0, 0, 25, 25)
    #FRAME_BUFFER.noSmooth()

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
    global INITIALIZED, magnetPort, magnetPort2, magnetPortAddresses, magnetPorts

    try:
        print("INITIALIZING")
        #for each in magnetPortAddresses:
        #    serialPort = Serial(this, each, 1000000) # ** is this baud rate correct?
        #   magnetPorts.append(serialPort)
        
        serialPort = Serial(this, magnetPortAddresses[0], 1000000)
        magnetPorts.append(serialPort)
        
        INITIALIZED = True
        print("ARDUINO SERIAL INITIALIZED")
    except:
        pass
        
def close_ports():
    # ** https://www.processing.org/reference/libraries/serial/Serial_stop_.html
    global INITIALIZED, magnetPorts

    if INITIALIZED:
        try:
            print("CLOSING PORTS")
            for p in magnetPorts:
                p.clear()
                p.stop()
        except:
            print("EXCEPTION in close_ports: ") # TODO catch and print the exception
    
    
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
    
    steps = 185
    
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

    # ** IMPROVEMENT: precompute and save the vertex data for all shapes in a single file so we can stop using openCV
    # ** and stop loading files in frame update
    global img_idx, morph_refresh, render, shape0, shape1, pset_0, cset_0, pset_1, pset_1, src_cv, det_cv
    
    render = []
    shape0 = []
    shape1 = []
    
    new_idx = randint(0, 999)

    # ** this function is called during draw(), so loading these files is probably causing the lag when a new shape is chosen
    src = loadImage("s" + str(img_idx) + ".png")
    det = loadImage("s" + str(new_idx) + ".png")
    
    # src.resize(500, 500)
    # det.resize(500, 500)
    
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
    
    g.removeCache(src)
    g.removeCache(det)
    morph_refresh = False
    img_idx = new_idx
