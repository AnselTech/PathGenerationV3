from MouseInterfaces.Hoverable import Hoverable
from SingletonState.SoftwareState import SoftwareState, Mode
from SingletonState.UserInput import UserInput
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef, Ref
from VisibleElements.FieldSurface import FieldSurface
from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
from Commands.Program import Program
import Utility
from typing import Iterator

import pygame

# Handle left clicks for dealing with the field
def handleLeftClick(state: SoftwareState, fieldSurface: FieldSurface, userInput: UserInput, program: Program):
    
    if userInput.isMouseOnField:

        # Add segment at mouse location
        if state.mode == Mode.ADD_SEGMENT:
            program.addPoint(userInput.mousePosition)

# Handle right clicks for dealing with the field
def handleRightClick(state: SoftwareState, userInput: UserInput):

    # If right click, cycle the mouse mode (excluding playback)
    if userInput.isMouseOnField:
        state.mode = state.mode.next()
        
# Handle zooming through mousewheel. Zoom "origin" should be at the mouse location
def handleMousewheel(fieldSurface: FieldSurface, fieldTransform: FieldTransform, userInput: UserInput) -> None:
    
    if not fieldSurface.isDragging and userInput.mousewheelDelta != 0:

        oldMouseX, oldMouseY = userInput.mousePosition.screenRef

        zoomDelta = userInput.mousewheelDelta * 0.1
        fieldTransform.zoom += zoomDelta

        # Pan to adjust for the translate that would result from the zoom
        panX, panY = fieldTransform.pan
        newMouseX, newMouseY = userInput.mousePosition.screenRef
        fieldTransform.pan = (panX + oldMouseX - newMouseX, panY + oldMouseY - newMouseY)


        fieldSurface.updateScaledSurface()


# If X is pressed and hovering over PathPoint/PathSegment, delete it
def handleDeleting(userInput: UserInput, state: SoftwareState):

    # Obviously, if X is not pressed, we're not deleting anything
    if not userInput.isKeyPressing(pygame.K_x):
        return


# Find the object that is hoverable, update that object's hoverable state, and return the object
def handleHoverables(state: SoftwareState, userInput: UserInput, hoverablesGenerator: Iterator[Hoverable]):

    if state.objectHovering is not None:
        state.objectHovering.resetHoverableObject()
        state.objectHovering = None

    for hoverableObject in hoverablesGenerator:
        obj: Hoverable = hoverableObject # just for type hinting
        if obj.checkIfHovering(userInput):
            state.objectHovering = obj
            obj.setHoveringObject()
            break

# Called when the mouse was just pressed and we want to see if a new object is cliked or about to be dragged
# If the object is draggable, drag it
# Elif object is clickable, click it
def handleStartingPressingObject(userInput: UserInput, state: SoftwareState, fieldSurface: FieldSurface) -> None:

    # if the mouse is down on some object, try to drag that object
    if isinstance(state.objectHovering, Draggable):
        state.objectDragged = state.objectHovering
        state.objectDragged._startDragging(userInput.mousePosition)
    elif isinstance(state.objectHovering, Clickable):
        objectClicked: Clickable = state.objectHovering # "cast" type hint to Clickable
        objectClicked.click()


# Determine what object is being dragged based on the mouse's rising and falling edges, and actually drag the object in question
# If the mouse is dragging but not on any particular object, it will pan the field
def handleDragging(userInput: UserInput, state: SoftwareState, fieldSurface: FieldSurface) -> None:

    if userInput.leftPressed and userInput.mousewheelDelta == 0: # left mouse button just pressed

        # When the mouse has just clicked on the object, nothing should have been dragging before        
        handleStartingPressingObject(userInput, state, fieldSurface)   
    
    elif userInput.mouseReleased: # released, so nothing should be dragged
        if state.objectDragged is not None: # there was an object being dragged, so release that
            state.objectDragged._stopDragging()
            state.objectDragged = None

    # Now that we know what's being dragged, actually drag the object
    if state.objectDragged is not None:
        changed = state.objectDragged.beDraggedByMouse(userInput)


        # if an object is being dragged it always takes precedence over any object that might be "hovering"
        if state.objectHovering is not state.objectDragged:
            if state.objectHovering is not None:
                state.objectHovering.resetHoverableObject()
            state.objectHovering = state.objectDragged
            state.objectHovering.setHoveringObject()
