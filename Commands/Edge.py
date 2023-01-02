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

    def __init__(self, program, edge):
        super().__init__()

        self.program = program
        self.edge = edge

        self.drawRadius = 4
        self.drawRadiusBig = 5
        self.hoverRadius = 20
        self.distanceToNode = 10

        self.heading = None

    def compute(self):
        nodePos: PointRef = self.edge.previous.position
        vector: VectorRef = VectorRef(Ref.FIELD, magnitude = self.distanceToNode, heading = self.heading)
        self.position: PointRef = nodePos + vector

    def beDraggedByMouse(self, userInput: UserInput):
        self.heading = Utility.thetaTwoPoints(self.edge.previous.position.fieldRef, userInput.mousePosition.fieldRef)
        
        # Snap to heading of previous edge if sufficiently close
        prevEdge = self.edge.previous.previous
        if prevEdge is not None and abs(prevEdge.afterHeading - self.heading) < 0.15:
            self.heading = prevEdge.afterHeading
        
        self.compute()
        self.program.recompute()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        print((self.position - userInput.mousePosition).magnitude(Ref.SCREEN))
        return Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef) < self.hoverRadius

    def draw(self, screen: pygame.Surface):
        graphics.drawThinLine(screen, colors.RED, *self.edge.previous.position.screenRef, *self.position.screenRef)
        r = self.drawRadiusBig if self.isHovering else self.drawRadius
        graphics.drawCircle(screen, *self.position.screenRef, colors.RED, r)

    

# linear
class StraightEdge(Edge):
    def __init__(self, program, previous: Node = None, next: Node = None):

        self.straightCommand: StraightCommand = StraightCommand(self)
        self.curveCommand: CurveCommand = CurveCommand(self)

        super().__init__(program, self.straightCommand, previous = previous, next = next)
        self.distance: float = None
        self.arc: Arc.Arc = Arc.Arc()
        self.headingPoint: HeadingPoint = HeadingPoint(program, self)

    def getMidpoint(self) -> PointRef:
        return self.previous.position + (self.next.position - self.previous.position) * 0.5
        

    def compute(self) -> float:

        if self.headingPoint.heading is None:
            if self.previous.previous is None:
                self.headingPoint.heading = self.previous.afterHeading
            else:
                self.headingPoint.heading = self.previous.previous.afterHeading

        self.headingPoint.compute()
        
        self.distance = Utility.distanceTuples(self.previous.position.fieldRef, self.next.position.fieldRef)
        
        self.arc.set(self.previous.position, self.next.position, self.headingPoint.heading)
        self.beforeHeading = self.arc.heading1
        self.afterHeading = self.arc.heading2
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

        if False: # draw line
            graphics.drawLine(screen, color, *self.previous.position.screenRef, *self.next.position.screenRef, thick)
        else: # draw curve
            
            graphics.drawArc(screen, color, self.arc.center.screenRef, self.arc.radius, self.arc.theta1, self.arc.theta2, self.arc.parity, thick+1)

        self.headingPoint.draw(screen)

        # Draw distance label text
        if isHovering:
            midpoint = self.getMidpoint().screenRef
            heading = (self.beforeHeading + self.afterHeading) / 2
            text = str(round(self.distance,2)) + "\""
            graphics.drawTextRotate(screen, graphics.FONT15, text, colors.BLACK, *midpoint, heading)
