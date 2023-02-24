from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
import pygame, graphics, Utility, colors, math
from Commands.Command import Command, TurnCommand, ShootCommand

class Node(Draggable, Clickable, ABC):

    def __init__(self, program, position: PointRef, hoverRadius: int, previous: 'Edge' = None, next: 'Edge' = None):

        super().__init__()

        self.previous: 'Edge' = previous
        self.next: 'Edge' = next

        self.program = program
        self.position: PointRef = position.copy()
        self.hoverRadius = hoverRadius

        self.arrowsEnabled = False


        self.command: Command = TurnCommand(self)


    def enableCoordinateArrows(self):
        print("enable coordinate")
        self.arrowsEnabled = True

    def disableCoordinateArrows(self):
        print("disable coordinate")
        self.arrowsEnabled = False


    # Called to determine if the mouse is touching this object (and if is the first object touched, would be considered hovered)
    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef)
        return distance < self.hoverRadius
    
    def click(self):
        self.program.state.nodeSelected = self
        self.enableCoordinateArrows()

    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        self.startMousePosition = userInput.mousePosition.copy()
        self.startNodePosition = self.position

    # snap to heading if close. return true if snapped
    def _snapToPosition(self, otherNode: 'Node', goalHeading: float, flip: bool = False):
        
        mouseHeading = Utility.thetaTwoPoints(otherNode.position.fieldRef, self.position.fieldRef)

        for h in [goalHeading, goalHeading + 3.1415]: # try both directions
            if Utility.headingDiff(mouseHeading, h) < 0.06:
                distance = Utility.distanceTuples(otherNode.position.fieldRef, self.position.fieldRef)
                vector = VectorRef(Ref.FIELD, magnitude = distance, heading = h)
                self.position = otherNode.position + vector
                return True

        return False

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):

        # if shift pressed, no snapping
        shiftPressed = userInput.isKeyPressing(pygame.K_LSHIFT)

        #self.position = userInput.mousePosition.copy()
        print((userInput.mousePosition - self.startMousePosition).fieldRef)
        self.position = self.startNodePosition + (userInput.mousePosition - self.startMousePosition)
        self.position.fieldRef = Utility.clamp2D(self.position.fieldRef, 0, 0, 144, 144)

        snapped = False

        # For straight edges only, snap to shoot heading of previous node
        if not shiftPressed and self.previous is not None and self.previous.arc.isStraight:
            node: Node = self.previous.previous
            if node.previous is not None and node.shoot.active:
                snapped = snapped or self._snapToPosition(node, node.shoot.heading)

        # For straight edges only, snap to shoot heading of next node
        if not shiftPressed and self.next is not None and self.next.arc.isStraight and self.next.next.shoot.active:
            nextNode = self.next.next
            snapped = snapped or self._snapToPosition(nextNode, nextNode.shoot.heading)

        # For straight edges only, snap to previous heading if close. Only for third node onward
        if not shiftPressed and self.previous is not None and self.previous.arc.isStraight:
            prevNode: Node = self.previous.previous
            if prevNode.previous is not None:
                snapped = snapped or self._snapToPosition(prevNode, prevNode.previous.afterHeading)
            else:
                snapped = snapped or self._snapToPosition(prevNode, prevNode.startHeading)

        # For straight edges only, snap to next heading if close
        if not shiftPressed and self.next is not None and self.next.arc.isStraight:

            nextNode = self.next.next

            if self.next.next.next is not None:
                snapped = snapped or self._snapToPosition(nextNode, nextNode.next.beforeHeading)
        
        # If has not been snapped already, snap to cardinal direction
        if not shiftPressed and not snapped:

            # Snap previous edge to cardinal direction
            if self.previous is not None and self.previous.arc.isStraight:
                prevNode = self.previous.previous
                snapped = snapped or self._snapToPosition(prevNode, 0)
                snapped = snapped or self._snapToPosition(prevNode, 3.1415/2)

            # Snap next edge to cardinal direction
            if not snapped and self.next is not None and self.next.arc.isStraight:
                nextNode = self.next.next
                snapped = snapped or self._snapToPosition(nextNode, 0)
                snapped = snapped or self._snapToPosition(nextNode, 3.1415/2)

        # For straight edges, change the heading of the edge rather than the arc's curvature (to maintain straightness)
        if self.previous is not None and self.previous.arc.isStraight:
            self.previous.headingPoint.setStraight()
            
        if self.next is not None and self.next.arc.isStraight:
            self.next.headingPoint.setStraight()

        self.program.recompute()

    def drawHovered(self, screen: pygame.Surface):

        if self.next is not None:
            graphics.drawGuideLine(screen, colors.GREEN, *self.position.screenRef, self.next.beforeHeading)

        if self.previous is not None:
            graphics.drawGuideLine(screen, colors.RED, *self.position.screenRef, self.previous.afterHeading)

    def compute(self):
        pass

    def draw(self, screen: pygame.Surface):

        pass