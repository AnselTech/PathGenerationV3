import pygame, sys
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef
import SingletonState.ReferenceFrame as ReferenceFrame
from SingletonState.SoftwareState import SoftwareState, Mode
from SingletonState.UserInput import UserInput
from VisibleElements.FieldSurface import FieldSurface
from MouseInteraction import *
from MouseInterfaces.TooltipOwner import TooltipOwner

from Commands.Program import Program
from MouseSelector.MouseSelector import MouseSelector

import Utility, colors
from typing import Iterator
import graphics
import multiprocessing as mp 

if __name__ == '__main__':

    # All the global singleton objects
    screen: pygame.Surface = pygame.display.set_mode((Utility.SCREEN_SIZE + Utility.PANEL_WIDTH, Utility.SCREEN_SIZE))
    pygame.display.set_caption("Path Generation 2.0 by Ansel")

    fieldTransform: FieldTransform = FieldTransform()
    ReferenceFrame.initFieldTransform(fieldTransform)

    fieldSurface: FieldSurface = FieldSurface(fieldTransform)
    userInput: UserInput = UserInput(pygame.mouse, pygame.key)
    program: Program = Program()

    state: SoftwareState = SoftwareState()
    mouseSelector: MouseSelector = MouseSelector(state)


def main():

    # Main software loop
    while True:
        
        userInput.getUserInput()
        if userInput.isQuit:
            pygame.quit()
            sys.exit()

        
        # Handle zooming with mousewheel
        handleMousewheel(fieldSurface, fieldTransform, userInput)
        
        # Find the hovered object out of all the possible hoverable objects
        handleHoverables(state, userInput, getHoverables())
        
        # Now that the hovered object is computed, handle what object is being dragged and then actually dragging the object
        handleDragging(userInput, state, fieldSurface)

        # If the X key is pressed, delete hovered PathPoint/segment
        handleDeleting(userInput, state)

        # Handle all field left click functionality
        if userInput.isMouseOnField:
            if userInput.leftClicked:
                handleLeftClick(state, fieldSurface)
            elif userInput.rightClicked:
                handleRightClick(state, userInput.mousePosition)

        # Draw everything on the screen
        drawEverything()
        
        

# Draw the vex field, full path, and panel
def drawEverything() -> None:
    
    # Draw the vex field
    fieldSurface.draw(screen)

    # Draw panel background
    border = 5
    pygame.draw.rect(screen, colors.PANEL_GREY, [Utility.SCREEN_SIZE + border, 0, Utility.PANEL_WIDTH - border, Utility.SCREEN_SIZE])
    pygame.draw.rect(screen, colors.BORDER_GREY, [Utility.SCREEN_SIZE, 0, border, Utility.SCREEN_SIZE])

    # Draw mouse selector buttons
    mouseSelector.draw(screen)

    # Draw a tooltip if there is one
    if state.objectHovering is not None and isinstance(state.objectHovering, TooltipOwner):
        state.objectHovering.drawTooltip(screen, userInput.mousePosition.screenRef)
        
    pygame.display.update()


# returns a generator object to iterate through all the hoverable objects,
# to determine which object is being hovered by the mouse in order
def getHoverables() -> Iterator[Hoverable]:

    # The points, segments, and field can only be hoverable if the mouse is on the field permieter and not on the panel
    if userInput.isMouseOnField:

        for hoverable in mouseSelector.getHoverables():
            yield hoverable
            
        yield fieldSurface
        
            

    else:
        pass

    # weird python hack to make it return an empty iterator if nothing hoverable
    return
    yield


if __name__ == '__main__':
    mp.freeze_support()
    main()