import pygame, math, pygame.gfxdraw, platform, os

pygame.font.init()

VERSION = "3.4.6"
VERSION_LOWER = "v" + VERSION.replace(".", "_")
IS_MAC: bool = platform.system() == "Darwin"

SAVE_TARGET = None
SAVE_TARGET_NAME = None

SCREEN_SIZE = 700
PANEL_WIDTH = 300

PIXELS_TO_FIELD_CORNER = 19 * (SCREEN_SIZE / 800)
FIELD_SIZE_IN_PIXELS = 766 * (SCREEN_SIZE / 800)
FIELD_SIZE_IN_INCHES = 144

def setTarget(target):
    global SAVE_TARGET, SAVE_TARGET_NAME
    SAVE_TARGET = target
    SAVE_TARGET_NAME = os.path.basename(target)[:-4]
    print(SAVE_TARGET, SAVE_TARGET_NAME)
    pygame.display.set_caption(f"Pathogen {VERSION} by Ansel [Target: {SAVE_TARGET}]")

def wrap(value, max):
    if value < 0:
        value += max
    elif value > max:
        value -= max
    return value

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
  
def scaleTuple(nums: tuple, scalar: float):
    return [i * scalar for i in nums]

def divideTuple(nums: tuple, scalar: float):
    return [i / scalar for i in nums]

def addTuples(tupleA: tuple, tupleB: tuple):
    assert len(tupleA) == len(tupleB)
    return [a+b for a,b in zip(tupleA, tupleB)]

def subtractTuples(tupleA: tuple, tupleB: tuple):
    assert len(tupleA) == len(tupleB)
    return [a-b for a,b in zip(tupleA, tupleB)]

def pixelsToInches(pixels):
    return (pixels / SCREEN_SIZE) * 144

def pixelsToTiles(pixels):
    return (pixels / SCREEN_SIZE) * 6

def clamp(value: float, minBound: float, maxBound: float) -> float:
    return max(minBound, min(maxBound, value))

def clamp2D(point: tuple, minX: float, minY: float, maxX: float, maxY: float) -> tuple:
    return clamp(point[0], minX, maxX), clamp(point[1], minY, maxY)

def hypo(s1, s2):
    return math.sqrt(s1*s1 + s2*s2)

def distance(x1,y1,x2,y2):
    return hypo(y2-y1, x2-x1)

def distanceTuples(vector1: tuple, vector2: tuple):
    return distance(*vector1, *vector2)

# Distance between point (x0, y0) and line (x1, y1,),(x2,y2)
# bad name
def distancePointToLine(x0, y0, x1, y1, x2, y2, signed: bool = False):
    ans = ((x2-x1)*(y1-y0) - (x1-x0)*(y2-y1)) / distance(x1, y1, x2, y2)
    if signed:
        return ans
    else:
        return abs(ans)

# Which side of the line the point is on.
# point (xp, yp), line at (xl, yl) with theta
def lineParity(xp, yp, xl, yl, theta):
    x1,y1 = xl - math.cos(theta), yl - math.sin(theta)
    return distancePointToLine(xp, yp, x1, y1, xl, yl, True) >= 0

def vector(x0, y0, theta, magnitude):
    return [x0 + magnitude*math.cos(theta), y0 + magnitude*math.sin(theta)]

def pointTouchingLine(mouseX: int, mouseY: int, x1: int, y1: int, x2: int, y2: int, lineHitboxThickness: int) -> bool:

    if x1 == x2 and y1 == y2:
        return False
    
    if distancePointToLine(mouseX,mouseY, x1, y1, x2, y2) <= lineHitboxThickness:
        dist = distance(x1, y1, x2, y2)
        if distance(mouseX, mouseY, x1, y1) < dist and distance(mouseX, mouseY, x2, y2) < dist:
            return True
    return False

# Vector projection algorithm
def pointOnLineClosestToPoint(pointX: int, pointY: int, firstX: int, firstY: int, secondX: int, secondY: int) -> tuple:
    ax = pointX - firstX
    ay = pointY - firstY
    bx = secondX - firstX
    by = secondY - firstY

    scalar = (ax * bx + ay * by) / (bx * bx + by * by)
    return [firstX + scalar * bx, firstY + scalar * by]

# Get the theta between positive x and the line from point A to point B
def thetaTwoPoints(pointA: tuple, pointB: tuple) -> float:
    return (math.atan2(pointB[1] - pointA[1], pointB[0] - pointA[0])) % (3.1415*2)

# Get the absolute heading (0 radians point up, clockwise positive) from A to B
def headingTwoPoints(pointA: tuple, pointB: tuple) -> float:
    return 3.1415 / 2.0 - thetaTwoPoints(pointA, pointB)

# Bound angle to between -pi and pi, preferring the smaller magnitude
def boundAngleRadians(angle: float) -> float:
    PI = 3.1415
    angle %= 2 * PI
    if angle < -PI:
        angle += 2*PI
    if angle > PI:
        angle -= 2*PI
    return angle
    
# Find the closest angle between two universal angles
def deltaInHeading(targetHeading: float, currentHeading: float) -> float:
    return boundAngleRadians(targetHeading - currentHeading)

def headingDiff(headingA: float, headingB: float):
    return abs(deltaInHeading(headingA, headingB))

def headingsEqual(headingA: float, headingB: float) -> bool:
    return abs(deltaInHeading(headingA, headingB)) < 0.001

# If parity == true, must return negative. if parity == false, must return positive.
def deltaInHeadingParity(targetHeading: float, currentHeading: float, parity: bool) -> float:
    diff = (targetHeading - currentHeading) % (3.1415*2)
    if parity and diff > 0:
        diff -= 3.1415*2
    elif not parity and diff < 0:
        diff += 3.1415*2
    return diff

def circleCenterFromThreePoints(x1, y1, x2, y2, x3, y3) -> tuple:
    x12 = x1 - x2
    x13 = x1 - x3
 
    y12 = y1 - y2
    y13 = y1 - y3
 
    y31 = y3 - y1
    y21 = y2 - y1
 
    x31 = x3 - x1
    x21 = x2 - x1
 
    # x1^2 - x3^2
    sx13 = pow(x1, 2) - pow(x3, 2)
 
    # y1^2 - y3^2
    sy13 = pow(y1, 2) - pow(y3, 2)
 
    sx21 = pow(x2, 2) - pow(x1, 2)
    sy21 = pow(y2, 2) - pow(y1, 2)
 
    f = (((sx13) * (x12) + (sy13) *
          (x12) + (sx21) * (x13) +
          (sy21) * (x13)) / (2 *
          ((y31) * (x12) - (y21) * (x13))))
             
    g = (((sx13) * (y12) + (sy13) * (y12) +
          (sx21) * (y13) + (sy21) * (y13)) /
          (2 * ((x31) * (y12) - (x21) * (y13))))
 
    c = (-pow(x1, 2) - pow(y1, 2) -
         2 * g * x1 - 2 * f * y1)
 
    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
    # where centre is (h = -g, k = -f) and
    # radius r as r^2 = h^2 + k^2 - c
    h = -g
    k = -f

    return h,k

# Given an initial theta and an offset x and y, calculate the other theta
# if (0,0) and (x,y) were two points of an arc with the initial theta
def thetaFromArc(theta1: float, dx: float, dy: float) -> float:
    return (2 * math.atan2(dy, dx) - theta1) % (3.1415*2)

# Given (x1,y1), (x2,y2), and the heading of (x1,y1), find the center of hte circle
def circleCenterFromTwoPointsAndTheta(x1, y1, x2, y2, theta) -> tuple:

    a = (x1 - x2) * math.cos(theta) + (y1 - y2) * math.sin(theta)
    b = (y1 - y2) * math.cos(theta) - (x1 - x2) * math.sin(theta)
    c = a / (2 * b)
    

    x = (x1+x2)/2 + c * (y1 - y2)
    y = (y1+y2)/2 + c * (x2 - x1)

    return x,y

def headingToString(headingRadians):
    headingRadians %= 3.1415*2
    return str(round(headingRadians * 180 / 3.1415, 1)) + u"\u00b0"