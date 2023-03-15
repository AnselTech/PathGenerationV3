import pygame, sys, os, os.path
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef
import SingletonState.ReferenceFrame as ReferenceFrame
from SingletonState.SoftwareState import SoftwareState, Mode
from SingletonState.UserInput import UserInput
from VisibleElements.FieldSurface import FieldSurface
from MouseInteraction import *
from MouseInterfaces.TooltipOwner import TooltipOwner
from RobotImage import RobotImage

from Commands.Program import Program
from Commands.Edge import Edge
from Commands.Command import *

import Commands.Node as Node
import Commands.StartNode as StartNode
import Commands.TurnNode as TurnNode

from Commands.OdomButton import OdomButton
from Commands.TextButton import TextButton
from Commands.SaveButton import SaveButton
from Commands.RobotButton import RobotButton
from Commands.ResetButton import ResetButton

import Commands.Between

from MouseSelector.MouseSelector import MouseSelector

import Utility, colors, math, time
from typing import Iterator
import graphics, Arc
import multiprocessing as mp 

if __name__ == '__main__':

    pygame.init()

    # All the global singleton objects
    screen: pygame.Surface = pygame.display.set_mode((Utility.SCREEN_SIZE + Utility.PANEL_WIDTH, Utility.SCREEN_SIZE))
    Utility.setTarget("Generated_Code.txt")

    fieldTransform: FieldTransform = FieldTransform()
    ReferenceFrame.initFieldTransform(fieldTransform)

    fieldSurface: FieldSurface = FieldSurface(fieldTransform)
    userInput: UserInput = UserInput(pygame.mouse, pygame.key)
    StartNode.init()
    TurnNode.init()
    
    Commands.Between.init()

    state: SoftwareState = SoftwareState()
    program: Program = Program(state)
    mouseSelector: MouseSelector = MouseSelector(state, program)
    robotImage: RobotImage = RobotImage(fieldTransform)

    odomButton: OdomButton = OdomButton(program)
    textButton: TextButton = TextButton(state)
    saveButton: SaveButton = SaveButton(program)
    robotButton: RobotButton = RobotButton(state)
    resetButton: ResetButton = ResetButton(program)

# attempt to load most recent .pg3 file and target
def loadPreviousSavestate():

    try:
        # Try to load .pg3 file
        with open("cache/autosave.pg3", "rb") as file:
            state: Serializer.State = pickle.load(file)
            state.load(program)
            print("Loaded autosaved .pg3 file.")
    except Exception as e:
        program.reset()
        print("Error with loading autosaved path:")
        print(e)

    try:
        # Try to load target
        with open("cache/autotarget.pgt", "rb") as file:
            data = pickle.load(file)
            target = data["target"]
            if os.path.isfile(target):
                Utility.setTarget(target)
                print("Loaded autosaved target location:", target)
            else:
                print("Autosaved target location is invalid. Defaulting target destination to Generated_Code.txt")
    except Exception as e:
        print("Error with loading target:")
        print(e)
        print("Defaulting target destination to Generated_Code.txt")
        Utility.setTarget("Generated_Code.txt")
        

def main():

    loadPreviousSavestate()

    AUTOSAVE_SECONDS = 60
    lastSave = time.time()

    while True:

        if time.time() - lastSave > AUTOSAVE_SECONDS:
            program.autosave()
            lastSave = time.time()
        
        userInput.getUserInput()
        if userInput.isQuit:

            program.generateSavefile() # save before quit

            pygame.quit()
            sys.exit()
        
        # Handle zooming with mousewheel
        modified = handleMousewheel(fieldSurface, fieldTransform, userInput, program)
        
        # Find the hovered object out of all the possible hoverable objects
        handleHoverables(state, userInput, getHoverables())
        
        # Now that the hovered object is computed, handle what object is being dragged and then actually dragging the object
        handleDragging(userInput, state, fieldSurface)

        # If the X key is pressed, delete hovered PathPoint/segment
        handleDeleting(userInput, state, program)

        handleCommandCommenting(userInput, state, program)

        # Handle dragging .pg3 file into program to load
        handleLoadedFile(program, userInput.loadedFile)

        shadowPos, shadowHeading = handleHoverPath(userInput, state, program)
        segmentShadow = handleHoverPathAdd(userInput, state, program)


        # Handle all field left click functionality
        if userInput.leftClicked:
            handleLeftClick(state, fieldSurface, userInput, program, segmentShadow)
        elif userInput.rightClicked:
            handleRightClick(state, userInput)

        if userInput.isKeyPressed(pygame.K_p):
            print(program.code)

        # Draw everything on the screen
        drawEverything(shadowPos, shadowHeading, segmentShadow)

                

# Draw the vex field, full path, and panel
def drawEverything(shadowPos: PointRef, shadowHeading: float, segmentShadow: PointRef) -> None:
    
    # Draw the vex field
    fieldSurface.draw(screen)

    if isinstance(state.objectHovering, Edge) or isinstance(state.objectHovering, Node.Node):
        state.objectHovering.drawHovered(screen)

    # Draw path specified by commands
    program.drawPath(screen, state)

    # Draw robot if mouse is hovering over point or line
    if shadowPos is not None and state.showRobot:
        robotImage.draw(screen, shadowPos, shadowHeading)

    if segmentShadow is not None:
        graphics.drawCircle(screen, *segmentShadow.screenRef, colors.BLACK, 4)

    drawShadow()

    program.drawSimulation(screen, robotImage)


    # Draw mouse selector buttons
    mouseSelector.draw(screen)

    # Draw interface buttons
    odomButton.draw(screen)
    textButton.draw(screen)
    saveButton.draw(screen)
    robotButton.draw(screen)
    resetButton.draw(screen)

    # Draw panel background
    border = 5
    pygame.draw.rect(screen, colors.PANEL_GREY, [Utility.SCREEN_SIZE + border, 0, Utility.PANEL_WIDTH - border, Utility.SCREEN_SIZE])
    pygame.draw.rect(screen, colors.BORDER_GREY, [Utility.SCREEN_SIZE, 0, border, Utility.SCREEN_SIZE])

    program.drawCommands(screen)

    # Draw a tooltip if there is one
    if state.objectHovering is not None and isinstance(state.objectHovering, TooltipOwner):
        state.objectHovering.drawTooltip(screen, userInput.mousePosition.screenRef)
        
    pygame.display.update()

def drawShadowSegment(fro: PointRef, to: PointRef):
    theta = Utility.thetaTwoPoints(fro.screenRef, to.screenRef)
    x,y = to.screenRef[0] + Utility.SCREEN_SIZE * math.cos(theta), to.screenRef[1] + Utility.SCREEN_SIZE * math.sin(theta)
    graphics.drawThinLine(screen, colors.GREEN, *to.screenRef, x, y)
    graphics.drawLine(screen, colors.BLACK, *fro.screenRef, *to.screenRef, 3, 140)
    graphics.drawCircle(screen, *to.screenRef, colors.BLACK, 5, 140)
    if state.showRobot:
        robotImage.draw(screen, to, Utility.thetaTwoPoints(fro.fieldRef, to.fieldRef))

def drawShadowArc(fro: PointRef, to: PointRef, heading1: float):

    arc = Arc.Arc(fro, to, heading1)

    graphics.drawGuideLine(screen, colors.BLACK, *arc.center.screenRef, arc.theta1)
    graphics.drawGuideLine(screen, colors.BLACK, *arc.center.screenRef, arc.theta2)

    graphics.drawGuideLine(screen, colors.RED, *fro.screenRef, arc.heading1)
    graphics.drawGuideLine(screen, colors.GREEN, *to.screenRef, arc.heading2)

    graphics.drawArc(screen, [80,80,80], arc.center.screenRef, arc.radius.screenRef, arc.theta1, arc.theta2, arc.parity, 3, 255)
    if state.showRobot:
        robotImage.draw(screen, to, arc.heading2)

def drawShadow():

    if state.objectHovering is not fieldSurface:
        return

    if state.mode == Mode.ADD_SEGMENT:

        fro = program.last.position
        to = userInput.mousePosition

        drawShadowSegment(fro, to)

    elif state.mode == Mode.ADD_CURVE:

        to, isStraight = program.snapNewPoint(userInput.mousePosition)
        fro = program.last.position

        if isStraight:
            drawShadowSegment(fro, to)
        elif Utility.distanceTuples(fro.fieldRef, to.fieldRef) > 0.1:

            if program.last.previous is None:
                heading1 = 0
            else:
                heading1 = program.last.previous.afterHeading

            drawShadowArc(fro, to, heading1)
            

# returns a generator object to iterate through all the hoverable objects,
# to determine which object is being hovered by the mouse in order
def getHoverables() -> Iterator[Hoverable]:

    # The points, segments, and field can only be hoverable if the mouse is on the field permieter and not on the panel
    if userInput.isMouseOnField:

        for hoverable in mouseSelector.getHoverables():
            yield hoverable

        yield odomButton
        yield textButton
        yield saveButton
        yield robotButton
        yield resetButton

        if not state.mode == Mode.PLAYBACK:
            for hoverable in program.getHoverablesPath(state):
                yield hoverable

        yield fieldSurface
    
    else:
        if not state.isCode:
            yield program.scroller
            for command in program.getHoverablesCommands():
                for hoverable in command.getHoverables():
                    yield hoverable
            for command in program.getHoverablesOther():
                yield command

    # weird python hack to make it return an empty iterator if nothing hoverable
    return
    yield


if __name__ == '__main__':
    mp.freeze_support()
    main()