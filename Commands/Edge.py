from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Draggable import Draggable
from Commands.Command import Command, StraightCommand, CurveCommand
from Node import Node
import pygame, pygame.gfxdraw, colors, graphics, Utility, math
from typing import Tuple

# Edges are not draggable. even curved edges are completely determined by node positions and starting theta
class Edge(Hoverable, ABC):
    def __init__(self, program, command: Command, previous: Node = None, next: Node = None):
        super().__init__()
        self.program = program

        self.previous: Node = previous
        self.next: Node = next

        self.beforeHeading = None
        self.afterHeading = None

        self.command: Command = command

    @abstractmethod
    def compute(self) -> float:
        pass

    @abstractmethod
    def drawHovered(self, screen: pygame.Surface):
        pass

    @abstractmethod
    def draw(screen: pygame.Surface):
        pass

class CurvePoint(Draggable):

    def __init__(self, edge):

        super().__init__()

        self.edge: 'StraightEdge' = edge

        self.curveDistance: float = 0
        self.curvePoint: PointRef = None

    def compute(self) -> Tuple[float, float]:

        previous, next = self.edge.previous, self.edge.next

        
        theta = Utility.thetaTwoPoints(previous.position.fieldRef, next.position.fieldRef) 
        self.curvePoint = self.edge.getMidpoint() + VectorRef(Ref.FIELD, magnitude = self.curveDistance, heading = theta + 3.1415/2)
        
        if self.curveDistance == 0:
            self.center: PointRef = None
            return theta, theta
        else:
            # find the center of the arc's circle
            p1 = previous.position.fieldRef
            p2 = self.curvePoint.fieldRef
            p3 = next.position.fieldRef
            fieldPos = Utility.circleCenterFromThreePoints(*p1, *p2, *p3)
            self.center: PointRef = PointRef(Ref.FIELD, fieldPos)

            heading1: float = Utility.thetaTwoPoints(p2, p1)
            heading2: float = Utility.thetaTwoPoints(p2, p3)

            if self.curveDistance > 0:
                return heading2, heading1
            else:
                return heading1, heading2


    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(self.curvePoint.screenRef, userInput.mousePosition.screenRef) < 10

    # Update curveDistance
    def beDraggedByMouse(self, userInput: UserInput):
        
        self.curveDistance = -Utility.distancePointToLine(
            *userInput.mousePosition.fieldRef,
            *self.edge.previous.position.fieldRef,
            *self.edge.next.position.fieldRef,
            True)

        # "snap" to linear
        if abs(self.curveDistance) < 2:
            self.curveDistance = 0

        self.edge.program.recompute()

    def draw(self, screen: pygame.Surface):
        radius = 5 if self.isHovering else 3
        graphics.drawCircle(screen, *self.curvePoint.screenRef, colors.RED, radius)


# linear
class StraightEdge(Edge):
    def __init__(self, program, previous: Node = None, next: Node = None):
        super().__init__(program, StraightCommand(self), previous = previous, next = next)
        self.distance: float = None
        self.curve: CurvePoint = CurvePoint(self)

    def getMidpoint(self) -> PointRef:
        return self.previous.position + (self.next.position - self.previous.position) * 0.5
        

    def compute(self) -> float:

        self.distance = Utility.distanceTuples(self.previous.position.fieldRef, self.next.position.fieldRef)
        self.beforeHeading, self.afterHeading = self.curve.compute(self.previous, self.next)
        
        return self.afterHeading

    # Check whether mouse is near the segment using a little math
    def checkIfHovering(self, userInput: UserInput) -> bool:
        a = self.previous.position.screenRef
        b = self.next.position.screenRef
        return Utility.pointTouchingLine(*userInput.mousePosition.screenRef, *a, *b, 13)

    def getClosestPoint(self, position: PointRef) -> PointRef:
        positionOnSegment = Utility.pointOnLineClosestToPoint(*position.fieldRef, *self.previous.position.fieldRef, *self.next.position.fieldRef)
        return PointRef(Ref.FIELD, positionOnSegment)

    def drawHovered(self, screen: pygame.Surface):

        graphics.drawGuideLine(screen, colors.GREEN, *self.next.position.screenRef, self.afterHeading)

        if not math.isclose(self.beforeHeading, self.afterHeading):
            graphics.drawGuideLine(screen, colors.RED, *self.previous.position.screenRef, self.beforeHeading)

    def draw(self, screen: pygame.Surface, drawCurvePoint: bool):

        isHovering = self.isHovering or self.command.isAnyHovering()

        # draw line between self.startPos and self.endPos
        if isHovering:
            color = colors.DARKBLUE
            thick = 4
        else:
            color = colors.BLACK
            thick = 3

        if self.curve.curveDistance == 0: # draw line
            graphics.drawLine(screen, color, *self.preivous.position.screenRef, *self.next.position.screenRef, thick)
        else: # draw curve
            center: PointRef = self.curve.center
            radius = Utility.distanceTuples(center.screenRef, self.curve.curvePoint.screenRef)

            pygame.draw.arc(screen, color, [center.screenRef[0] - radius, center.screenRef[1] - radius, radius*2, radius*2], self.beforeHeading, self.afterHeading, thick+1)

        # Draw curve point
        if drawCurvePoint:
            self.curve.draw(screen)

        # Draw distance label text
        if isHovering:
            midpoint = self.getMidpoint().screenRef
            heading = (self.beforeHeading+self.afterHeading) / 2
            text = str(round(self.distance,2)) + "\""
            graphics.drawTextRotate(screen, graphics.FONT15, text, colors.BLACK, *midpoint, heading)
