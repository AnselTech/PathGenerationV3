from MouseInterfaces.Hoverable import Hoverable
from SingletonState.SoftwareState import SoftwareState, Mode
from SingletonState.UserInput import UserInput
from SingletonState.FieldTransform import FieldTransform
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from VisibleElements.FieldSurface import FieldSurface
from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
from Commands.Program import Program
from Commands.StartNode import StartNode
from Commands.Edge import StraightEdge
from Commands.Node import Node
from Commands.TurnNode import TurnNode
import Commands.Serializer as Serializer
import Utility
from typing import Iterator, Tuple
from Arc import Arc
import pickle
import pygame

# Handle left clicks for dealing with the field
def handleLeftClick(state: SoftwareState, fieldSurface: FieldSurface, userInput: UserInput, program: Program, segmentShadow: PointRef):

    # Add segment at mouse location if mouse if clicking at some area of the field
    if state.objectHovering == fieldSurface:
        if state.mode == Mode.ADD_SEGMENT:
            program.addNodeForward(userInput.mousePosition)
        elif state.mode == Mode.ADD_CURVE:
            program.addNodeCurve(userInput.mousePosition)

    elif segmentShadow is not None:
        program.insertNode(state.objectHovering, segmentShadow)
    

# Handle right clicks for dealing with the field
def handleRightClick(state: SoftwareState, userInput: UserInput):

    # If right click, cycle the mouse mode (excluding playback)
    if isinstance(state.objectHovering, TurnNode) and state.mode != Mode.MOUSE_SELECT:
        node: Node = state.objectHovering
        node.shoot.active = not node.shoot.active
        node.program.recompute()
    elif type(state.objectHovering) == StraightEdge:
        state.objectHovering.toggleReversed() # toggle going forward/reverse on edge
    elif type(state.objectHovering) == FieldSurface:
        state.mode = state.mode.next()
        
# Handle zooming through mousewheel. Zoom "origin" should be at the mouse location
# return true if modified
def handleMousewheel(fieldSurface: FieldSurface, fieldTransform: FieldTransform, userInput: UserInput) -> bool:
    
    if not fieldSurface.isDragging and userInput.mousewheelDelta != 0:

        oldMouseX, oldMouseY = userInput.mousePosition.screenRef

        zoomDelta = userInput.mousewheelDelta * 0.1
        fieldTransform.zoom += zoomDelta

        # Pan to adjust for the translate that would result from the zoom
        panX, panY = fieldTransform.pan
        newMouseX, newMouseY = userInput.mousePosition.screenRef
        fieldTransform.pan = (panX + oldMouseX - newMouseX, panY + oldMouseY - newMouseY)


        fieldSurface.updateScaledSurface()
        return True

    return False


# If X is pressed and hovering over PathPoint/PathSegment, delete it
def handleDeleting(userInput: UserInput, state: SoftwareState, program: Program):

    # Obviously, if X is not pressed, we're not deleting anything
    if not userInput.isKeyPressing(pygame.K_x):
        return

    # can only delete turn nodes, not edges or first node
    if type(state.objectHovering) == TurnNode:
        program.deleteNode(state.objectHovering)


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
        state.objectDragged._startDragging(userInput)

    elif isinstance(state.objectHovering, Clickable):
        objectClicked: Clickable = state.objectHovering
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
        state.objectDragged.beDraggedByMouse(userInput)


        # if an object is being dragged it always takes precedence over any object that might be "hovering"
        if state.objectHovering is not state.objectDragged:
            if state.objectHovering is not None:
                state.objectHovering.resetHoverableObject()
            state.objectHovering = state.objectDragged
            state.objectHovering.setHoveringObject()

# return (position, heading)
def getPointOnEdge(state: SoftwareState, edge: StraightEdge, position: PointRef) -> Tuple[PointRef, float]:
    
    invert = 3.1415 if edge.reversed else 0
    
    # Straight. Find closest point on line
    if edge.arc.isStraight:
        return state.objectHovering.getClosestPoint(position), edge.beforeHeading + invert
    else:
        # Curved. Find closest point on arc
        arc: Arc = edge.arc
        theta = Utility.thetaTwoPoints(arc.center.fieldRef, position.fieldRef)
        heading = theta + 3.1415/2 * (-1 if arc.parity else 1)
        return arc.center + VectorRef(Ref.FIELD, magnitude = arc.radius.fieldRef, heading = theta), heading + invert


def handleHoverPath(userInput: UserInput, state: SoftwareState, program: Program) -> Tuple[PointRef, float]:


    if state.mode == Mode.MOUSE_SELECT:

        if type(state.objectHovering) == StraightEdge:
            return getPointOnEdge(state, state.objectHovering, userInput.mousePosition)
        elif type(state.objectHovering) == StartNode:
            if state.objectHovering.next is not None:
                pos = state.objectHovering.position
                heading = state.objectHovering.next.beforeHeading
                return pos, heading
        elif type(state.objectHovering) == TurnNode:
            pos = state.objectHovering.position
            heading = state.objectHovering.previous.afterHeading
            return pos, heading
    return None, None

def handleHoverPathAdd(userInput: UserInput, state: SoftwareState, program: Program) -> PointRef:

    if state.mode == Mode.ADD_SEGMENT or state.mode == Mode.ADD_CURVE:
        if type(state.objectHovering) == StraightEdge:
            return getPointOnEdge(state, state.objectHovering, userInput.mousePosition)[0]
    return None

# When a .pg3 save file dragged into the screen, load all the data into the program
def handleLoadedFile(program: Program, filename):
    if filename is None:
        return

    if filename.endswith(".pg3"):
        with open(filename, "rb") as file:
            state: Serializer.State = pickle.load(file)
            state.load(program)