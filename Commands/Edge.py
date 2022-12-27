from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Draggable import Draggable
from Commands.Command import Command, StraightCommand, CurveCommand
import pygame, pygame.gfxdraw, colors, graphics, Utility

# Edges are not draggable. even curved edges are completely determined by node positions and starting theta
class Edge(Hoverable, ABC):
    def __init__(self, command: Command):
        super().__init__()
        self.beforePos: PointRef = None
        self.afterPos: PointRef = None

        self.command: Command = command

    @abstractmethod
    def compute(self, beforeHeading: float) -> float:
        pass

    @abstractmethod
    def drawHovered(self, screen: pygame.Surface):
        pass

    @abstractmethod
    def draw(screen: pygame.Surface):
        pass

class CurvePoint(Draggable):

    def __init__(self, edge: 'Edge'):

        super().__init__()

        self.edge: 'Edge' = edge
        self.curveDistance: float = 0
        self.curvePoint: PointRef = None

    def compute(self):
        midpoint: PointRef = self.edge.beforePos + (self.edge.afterPos - self.edge.beforePos) * 0.5
        self.curvePoint = midpoint + VectorRef(Ref.FIELD, magnitude = self.curveDistance, heading = self.edge.heading + 3.1415/2)
        
        if self.curveDistance == 0:
            self.center: PointRef = None
        else:
            # find the center of the arc's circle
            p1 = self.edge.beforePos.fieldRef
            p2 = self.curvePoint.fieldRef
            p3 = self.edge.afterPos.fieldRef
            fieldPos = Utility.circleCenterFromThreePoints(*p1, *p2, *p3)
            self.center: PointRef = PointRef(Ref.FIELD, fieldPos)


    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(self.curvePoint.screenRef, userInput.mousePosition.screenRef) < 10

    # Update curveDistance
    def beDraggedByMouse(self, userInput: UserInput):
        
        self.curveDistance = -Utility.distancePointToLine(
            *userInput.mousePosition.fieldRef,
            *self.edge.beforePos.fieldRef,
            *self.edge.afterPos.fieldRef,
            True)

        # "snap" to linear
        if abs(self.curveDistance) < 2:
            self.curveDistance = 0

        self.compute()

    def draw(self, screen: pygame.Surface):
        radius = 5 if self.isHovering else 3
        graphics.drawCircle(screen, *self.curvePoint.screenRef, colors.RED, radius)


# linear
class StraightEdge(Edge):
    def __init__(self):
        super().__init__(StraightCommand(self))
        self.distance: float = None
        self.curve: CurvePoint = CurvePoint(self)
        

    def compute(self, beforeHeading: float, beforePos: PointRef, afterPos: PointRef) -> float:
        self.heading = beforeHeading
        self.beforePos = beforePos
        self.afterPos = afterPos
        self.distance = Utility.distanceTuples(beforePos.fieldRef, afterPos.fieldRef)

        self.curve.compute()
        
        return self.heading

    # Check whether mouse is near the segment using a little math
    def checkIfHovering(self, userInput: UserInput) -> bool:
        a = self.beforePos.screenRef
        b = self.afterPos.screenRef
        return Utility.pointTouchingLine(*userInput.mousePosition.screenRef, *a, *b, 13)

    def getClosestPoint(self, position: PointRef) -> PointRef:
        positionOnSegment = Utility.pointOnLineClosestToPoint(*position.fieldRef, *self.beforePos.fieldRef, *self.afterPos.fieldRef)
        return PointRef(Ref.FIELD, positionOnSegment)

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.GREEN, *self.beforePos.screenRef, self.heading)

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
            graphics.drawLine(screen, color, *self.beforePos.screenRef, *self.afterPos.screenRef, thick)
        else: # draw curve
            center: PointRef = self.curve.center
            theta1: float = -Utility.thetaTwoPoints(center.fieldRef, self.beforePos.fieldRef) * 180 / 3.1415
            theta2: float = -Utility.thetaTwoPoints(center.fieldRef, self.afterPos.fieldRef) * 180 / 3.1415

            if self.curve.curveDistance < 0:
                theta1, theta2 = theta2, theta1    
        
            radius = Utility.distanceTuples(center.screenRef, self.curve.curvePoint.screenRef)
            pygame.gfxdraw.arc(screen, int(center.screenRef[0]), int(center.screenRef[1]), int(radius), int(theta1), int(theta2), color)

        # Draw curve point
        if drawCurvePoint:
            self.curve.draw(screen)

        # Draw distance label text
        if isHovering:
            midpoint: PointRef = self.beforePos + (self.afterPos - self.beforePos)*0.5
            graphics.drawTextRotate(screen, graphics.FONT15, str(round(self.distance,2)) + "\"", colors.BLACK, *midpoint.screenRef, self.heading)

# circular arc
class CurveEdge(Edge):
    def __init__(self):
        super().__init__(CurveCommand(self))
        self.beforeHeading = None
        self.afterHeading = None

    def compute(self, beforeHeading: float) -> float:
        pass

    def drawHovered(self, screen: pygame.Surface):
        pass
        
    # Given before and after positions, as well as before heading, update afterHeading based on circular arc
    def computeAfterHeading(self):
        #TODO
        pass