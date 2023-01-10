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

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):

        self.position = userInput.mousePosition.copy()

        # For straight edges only, snap to previous heading if close. Only for third node onward
        if self.previous is not None and self.previous.arc.isStraight and self.previous.previous.previous is not None:
            prevNode = self.previous.previous
            mouseHeading = Utility.thetaTwoPoints(prevNode.position.fieldRef, self.position.fieldRef)
            previousHeading = prevNode.previous.afterHeading
            if Utility.headingDiff(mouseHeading, previousHeading) < 0.06:
                distance = Utility.distanceTuples(prevNode.position.fieldRef, self.position.fieldRef)
                self.position = prevNode.position + VectorRef(Ref.FIELD, magnitude = distance, heading = previousHeading)
            elif Utility.headingDiff(mouseHeading, previousHeading + 3.1415) < 0.06:
                distance = Utility.distanceTuples(prevNode.position.fieldRef, self.position.fieldRef)
                self.position = prevNode.position + VectorRef(Ref.FIELD, magnitude = distance, heading = previousHeading + 3.1415)

        # For straight edges only, snap to next heading if close
        if self.next is not None and self.next.arc.isStraight and self.next.next.next is not None:
            nextNode = self.next.next
            mouseHeading = Utility.thetaTwoPoints(self.position.fieldRef, nextNode.position.fieldRef)
            nextHeading = nextNode.next.beforeHeading
            if Utility.headingDiff(mouseHeading, nextHeading) < 0.06:
                distance = Utility.distanceTuples(nextNode.position.fieldRef, self.position.fieldRef)
                self.position = nextNode.position - VectorRef(Ref.FIELD, magnitude = distance, heading = nextHeading)
            if Utility.headingDiff(mouseHeading, nextHeading + 3.1415) < 0.06:
                distance = Utility.distanceTuples(nextNode.position.fieldRef, self.position.fieldRef)
                self.position = nextNode.position - VectorRef(Ref.FIELD, magnitude = distance, heading = nextHeading + 3.1415)


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