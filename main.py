import pygame, sys
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

from MouseSelector.MouseSelector import MouseSelector

import Utility, colors, math
from typing import Iterator
import graphics
import multiprocessing as mp 

if __name__ == '__main__':

    pygame.init()

    # All the global singleton objects
    screen: pygame.Surface = pygame.display.set_mode((Utility.SCREEN_SIZE + Utility.PANEL_WIDTH, Utility.SCREEN_SIZE))
    pygame.display.set_caption("Path Generation 3.0 by Ansel")

    fieldTransform: FieldTransform = FieldTransform()
    ReferenceFrame.initFieldTransform(fieldTransform)

    fieldSurface: FieldSurface = FieldSurface(fieldTransform)
    userInput: UserInput = UserInput(pygame.mouse, pygame.key)
    StartNode.init()
    TurnNode.init()
    program: Program = Program()

    state: SoftwareState = SoftwareState()
    mouseSelector: MouseSelector = MouseSelector(state)
    robotImage: RobotImage = RobotImage(fieldTransform)


def main():

    # Main software loop
    while True:
        
        userInput.getUserInput()
        if userInput.isQuit:
            pygame.quit()
            sys.exit()
        
        # Handle zooming with mousewheel
        modified = handleMousewheel(fieldSurface, fieldTransform, userInput)
        
        # Find the hovered object out of all the possible hoverable objects
        handleHoverables(state, userInput, getHoverables())
        
        # Now that the hovered object is computed, handle what object is being dragged and then actually dragging the object
        handleDragging(userInput, state, fieldSurface)

        # If the X key is pressed, delete hovered PathPoint/segment
        handleDeleting(userInput, state, program)

        shadowPos, shadowHeading = handleHoverPath(userInput, state, program)
        segmentShadow = handleHoverPathAdd(userInput, state, program)


        # Handle all field left click functionality
        if userInput.isMouseOnField:
            if userInput.leftClicked:
                handleLeftClick(state, fieldSurface, userInput, program, segmentShadow)
            elif userInput.rightClicked:
                handleRightClick(state, userInput)

        if userInput.isKeyPressed(pygame.K_p):
            print(program.getCode())

        # Draw everything on the screen
        drawEverything(shadowPos, shadowHeading, segmentShadow)

                

# Draw the vex field, full path, and panel
def drawEverything(shadowPos: PointRef, shadowHeading: float, segmentShadow: PointRef) -> None:
    
    # Draw the vex field
    fieldSurface.draw(screen)

    if isinstance(state.objectHovering, Edge) or isinstance(state.objectHovering, Node.Node):
        state.objectHovering.drawHovered(screen)

    # Draw path specified by commands
    program.drawPath(screen, state.mode == Mode.ADD_CURVE)

    # Draw robot if mouse is hovering over point or line
    if shadowPos is not None:
        robotImage.draw(screen, shadowPos, shadowHeading)

    if segmentShadow is not None:
        graphics.drawCircle(screen, *segmentShadow.screenRef, colors.BLACK, 4)

    drawShadow()


    # Draw mouse selector buttons
    mouseSelector.draw(screen)

    # Draw panel background
    border = 5
    pygame.draw.rect(screen, colors.PANEL_GREY, [Utility.SCREEN_SIZE + border, 0, Utility.PANEL_WIDTH - border, Utility.SCREEN_SIZE])
    pygame.draw.rect(screen, colors.BORDER_GREY, [Utility.SCREEN_SIZE, 0, border, Utility.SCREEN_SIZE])

    program.drawCommands(screen)

    # Draw a tooltip if there is one
    if state.objectHovering is not None and isinstance(state.objectHovering, TooltipOwner):
        state.objectHovering.drawTooltip(screen, userInput.mousePosition.screenRef)
        
    pygame.display.update()

def drawShadow():

    if state.objectHovering is not fieldSurface:
        return

    if state.mode != Mode.ADD_SEGMENT:
        return

    toPos = program.snapNewPoint(userInput.mousePosition)

    fro = program.last.position.screenRef
    to = toPos.screenRef
    theta = Utility.thetaTwoPoints(fro, to)
    x,y = to[0] + Utility.SCREEN_SIZE * math.cos(theta), to[1] + Utility.SCREEN_SIZE * math.sin(theta)
    graphics.drawThinLine(screen, colors.GREEN, *to, x, y)
    graphics.drawLine(screen, colors.BLACK, *fro, *to, 3, 140)
    graphics.drawCircle(screen, *to, colors.BLACK, 5, 140)

    robotImage.draw(screen, toPos, -theta)
    


# returns a generator object to iterate through all the hoverable objects,
# to determine which object is being hovered by the mouse in order
def getHoverables() -> Iterator[Hoverable]:

    # The points, segments, and field can only be hoverable if the mouse is on the field permieter and not on the panel
    if userInput.isMouseOnField:

        for hoverable in mouseSelector.getHoverables():
            yield hoverable

        for hoverable in program.getHoverablesPath(state.mode == Mode.ADD_CURVE):
            yield hoverable

        yield fieldSurface
    
    else:
        for command in program.getHoverablesCommands():
            for hoverable in command.getHoverables():
                yield hoverable

    # weird python hack to make it return an empty iterator if nothing hoverable
    return
    yield


if __name__ == '__main__':
    mp.freeze_support()
    main()