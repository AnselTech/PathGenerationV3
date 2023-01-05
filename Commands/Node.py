from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
import pygame, graphics, Utility, colors, math
from Commands.Command import Command, TurnCommand

# Every node has the option to shoot discs into the target goal.
# Right click to toggle shooting. Visually appears as a yellow vector
# Draggable to adjust aim
class Shoot(Draggable):

    def __init__(self, program, parent: 'Node'):

        super().__init__()

        self.program = program
        self.parent: 'Node' = parent

        self.target: PointRef = PointRef(Ref.FIELD, point = (132, 132)) # red goal center

        self.active = False
        self.headingCorrection = 0 # [Heading to goal] + self.headingCorrection gives shooting heading
        self.heading = None
        self.magnitude = 10 # magnitude of vector in pixels
        self.hoverRadius = 10

    def compute(self):
        self.heading: float = (self.target - self.parent.position).theta() + self.headingCorrection
        self.position: PointRef = self.parent.position + VectorRef(Ref.FIELD, magnitude = self.magnitude, heading = self.heading)
        vector: VectorRef = (self.position - self.parent.position)
        self.hoverPosition1: PointRef = self.parent.position + vector * 0.5
        self.hoverPosition2: PointRef = self.parent.position + vector * 1.2
        print(self.parent.position.fieldRef)

    # Hovering if touching the top half of the vector
    def checkIfHovering(self, userInput: UserInput) -> bool:

        if not self.active:
            return False

        return Utility.pointTouchingLine(
            *userInput.mousePosition.screenRef,
            *self.hoverPosition1.screenRef,
            *self.hoverPosition2.screenRef,
            self.hoverRadius
        )

    # Adjust headingCorrection based on where the mouse is dragging the arrow
    def beDraggedByMouse(self, userInput: UserInput):
        mouseHeading = Utility.thetaTwoPoints(self.parent.position.fieldRef, userInput.mousePosition.fieldRef)
        shootHeading = (self.target - self.parent.position).theta()
        self.headingCorrection = Utility.deltaInHeading(mouseHeading, shootHeading)
        self.program.recompute()

    def draw(self, screen: pygame.Surface, color: tuple, thick: bool):
        thickness = 5 if thick else 3
        a = 2 if thick else 1.6
        graphics.drawVector(screen, color, *self.parent.position.screenRef, *self.position.screenRef, thickness, a)


class Node(Draggable, ABC):

    def __init__(self, program, position: PointRef, hoverRadius: int, previous: 'Edge' = None, next: 'Edge' = None):

        super().__init__()

        self.previous: 'Edge' = previous
        self.next: 'Edge' = next

        self.program = program
        self.position: PointRef = position.copy()
        self.hoverRadius = hoverRadius

        self.shoot: Shoot = Shoot(program, self)


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
        self.shoot.compute()

    def draw(self, screen: pygame.Surface):

        thick = False

        if self.shoot.active:
            color = (255,230,0)
            if self.shoot.isHovering:
                thick = True
        elif self.isHovering:
            color = (255,215,0,150)

        if self.shoot.active or self.isHovering:
            self.shoot.draw(screen, color, thick)