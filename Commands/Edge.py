from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Draggable import Draggable
from Commands.Command import Command, StraightCommand, CurveCommand
from Commands.Node import Node
import pygame, pygame.gfxdraw, colors, graphics, Utility, math, Arc
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

# A draggable point used to set heading1 of StraightEge
class HeadingPoint(Draggable):

    def __init__(self, program, edge, heading = None):
        super().__init__()

        self.program = program
        self.edge: 'StraightEdge' = edge

        self.drawRadius = 4
        self.drawRadiusBig = 5
        self.hoverRadius = 20
        self.distanceToNode = 10

        self.heading = heading

    def setStraight(self):
        fro: PointRef = self.edge.previous.position
        to: PointRef = self.edge.next.position
        self.heading = Utility.thetaTwoPoints(fro.fieldRef, to.fieldRef)

    def compute(self):
        nodePos: PointRef = self.edge.previous.position
        vector: VectorRef = VectorRef(Ref.FIELD, magnitude = self.distanceToNode, heading = self.heading)
        self.position: PointRef = nodePos + vector

    def beDraggedByMouse(self, userInput: UserInput):
        self.heading = Utility.thetaTwoPoints(self.edge.previous.position.fieldRef, userInput.mousePosition.fieldRef)
        
        # Snap to straight edge if sufficiently close
        if Utility.headingDiff(self.edge.straightHeading, self.heading) < 0.12:
            self.heading = self.edge.straightHeading

        # Snap to heading of previous edge if sufficiently close
        prevEdge: 'StraightEdge' = self.edge.previous.previous
        if prevEdge is not None and Utility.headingDiff(prevEdge.afterHeading, self.heading) < 0.12:
            self.heading = prevEdge.afterHeading

        # Snap to heading of next edge if suffiently close
        nextEdge: 'StraightEdge' = self.edge.next.next
        heading2 = Arc.Arc(self.edge.previous.position, self.edge.next.position, self.heading).heading2
        if nextEdge is not None and Utility.headingDiff(nextEdge.beforeHeading, heading2) < 0.12:
            dx = self.edge.next.position.fieldRef[0] - self.edge.previous.position.fieldRef[0]
            dy = self.edge.next.position.fieldRef[1] - self.edge.previous.position.fieldRef[1]
            self.heading = Utility.thetaFromArc(nextEdge.beforeHeading, dx, dy)
        
        self.compute()
        self.program.recompute()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef) < self.hoverRadius

    def draw(self, screen: pygame.Surface):
        graphics.drawThinLine(screen, colors.RED, *self.edge.previous.position.screenRef, *self.position.screenRef)
        r = self.drawRadiusBig if self.isHovering else self.drawRadius
        graphics.drawCircle(screen, *self.position.screenRef, colors.RED, r)

    

# linear
class StraightEdge(Edge):
    def __init__(self, program, previous: Node = None, next: Node = None, heading1: float = None):

        self.straightCommand: StraightCommand = StraightCommand(self)
        self.curveCommand: CurveCommand = CurveCommand(self)

        super().__init__(program, self.straightCommand, previous = previous, next = next)
        self.distance: float = None
        self.arc: Arc.Arc = Arc.Arc()
        self.headingPoint: HeadingPoint = HeadingPoint(program, self, heading1)
        
        self.distance = None
        self.straightHeading = None


    def getMidpoint(self) -> PointRef:
        return self.previous.position + (self.next.position - self.previous.position) * 0.5
        

    def compute(self) -> float:

        self.straightHeading = Utility.thetaTwoPoints(self.previous.position.fieldRef, self.next.position.fieldRef)

        self.headingPoint.compute()
        
        self.distance = Utility.distanceTuples(self.previous.position.fieldRef, self.next.position.fieldRef)
        self.distanceStr = str(round(self.distance,1)) + "\""

        self.arc.set(self.previous.position, self.next.position, self.headingPoint.heading)
        self.beforeHeading = self.arc.heading1
        self.afterHeading = self.arc.heading2

        self.beforeHeadingStr = str(round(self.beforeHeading * 180 / 3.1415,1)) + u"\u00b0"
        self.afterHeadingStr = str(round(self.afterHeading * 180 / 3.1415,1)) + u"\u00b0"
        if not self.arc.isStraight:
            deltaTheta = Utility.deltaInHeadingParity(self.arc.theta2, self.arc.theta1, self.arc.parity)
            arcLength = abs(deltaTheta) * self.arc.radius
            self.arcLengthStr = str(round(arcLength, 1)) + "\""

        self.command = self.straightCommand if self.arc.isStraight else self.curveCommand

        return self.afterHeading

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return self.arc.isTouching(userInput.mousePosition)

    def getClosestPoint(self, position: PointRef) -> PointRef:
        positionOnSegment = Utility.pointOnLineClosestToPoint(*position.fieldRef, *self.previous.position.fieldRef, *self.next.position.fieldRef)
        return PointRef(Ref.FIELD, positionOnSegment)

    def drawHovered(self, screen: pygame.Surface):
        
        x = self.next.position.fieldRef[0] - self.previous.position.fieldRef[0]
        y = self.next.position.fieldRef[1] - self.previous.position.fieldRef[1]

        graphics.drawGuideLine(screen, colors.GREEN, *self.next.position.screenRef, self.afterHeading)

        if not math.isclose(self.beforeHeading, self.afterHeading):
            graphics.drawGuideLine(screen, colors.RED, *self.previous.position.screenRef, self.beforeHeading)

    def draw(self, screen: pygame.Surface):

        isHovering = self.isHovering or self.command.isAnyHovering()

        # draw line between self.startPos and self.endPos
        if isHovering:
            color = colors.DARKBLUE
            thick = 4
        else:
            color = colors.BLACK
            thick = 3

        if self.arc.isStraight: # draw line
            graphics.drawLine(screen, color, *self.previous.position.screenRef, *self.next.position.screenRef, thick)
        else: # draw curve
            graphics.drawArc(screen, color, self.arc.center.screenRef, self.arc.radius, self.arc.theta1, self.arc.theta2, self.arc.parity, thick+1)

        self.headingPoint.draw(screen)

        # Draw distance label text
        if isHovering:
            midpoint = self.getMidpoint().screenRef
            heading = (self.beforeHeading + self.afterHeading) / 2
            graphics.drawTextRotate(screen, graphics.FONT15, self.distanceStr, colors.BLACK, *midpoint, heading)
