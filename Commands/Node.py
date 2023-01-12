from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
import pygame, graphics, Utility, colors, math
from Commands.Command import Command, TurnCommand, ShootCommand

class Node(Draggable, ABC):

    def __init__(self, program, position: PointRef, hoverRadius: int, previous: 'Edge' = None, next: 'Edge' = None):

        super().__init__()

        self.previous: 'Edge' = previous
        self.next: 'Edge' = next

        self.program = program
        self.position: PointRef = position.copy()
        self.hoverRadius = hoverRadius


        self.command: Command = TurnCommand(self)


    # Called to determine if the mouse is touching this object (and if is the first object touched, would be considered hovered)
    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef)
        return distance < self.hoverRadius

    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass

    def _snapToPosition(self, otherNode: 'Node', goalHeading: float, flip: bool = False):
        mouseHeading = Utility.thetaTwoPoints(otherNode.position.fieldRef, self.position.fieldRef)

        for h in [goalHeading, goalHeading + 3.1415]: # try both directions
            if Utility.headingDiff(mouseHeading, h) < 0.06:
                distance = Utility.distanceTuples(otherNode.position.fieldRef, self.position.fieldRef)
                vector = VectorRef(Ref.FIELD, magnitude = distance, heading = h)
                self.position = otherNode.position + vector
                break

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):

        self.position = userInput.mousePosition.copy()

        # For straight edges only, snap to shoot heading of previous node
        if self.previous is not None and self.previous.arc.isStraight:
            node: Node = self.previous.previous
            if node.previous is not None and node.shoot.active:
                self._snapToPosition(node, node.shoot.heading)

        # For straight edges only, snap to shoot heading of next node
        if self.next is not None and self.next.arc.isStraight and self.next.next.shoot.active:
            nextNode = self.next.next
            self._snapToPosition(nextNode, nextNode.shoot.heading)

        # For straight edges only, snap to previous heading if close. Only for third node onward
        if self.previous is not None and self.previous.arc.isStraight and self.previous.previous.previous is not None:
            prevNode: Node = self.previous.previous
            self._snapToPosition(prevNode, prevNode.previous.afterHeading)

        # For straight edges only, snap to next heading if close
        if self.next is not None and self.next.arc.isStraight and self.next.next.next is not None:
            nextNode = self.next.next
            self._snapToPosition(nextNode, nextNode.next.beforeHeading)

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