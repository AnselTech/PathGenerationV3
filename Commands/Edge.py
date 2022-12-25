from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef
from SingletonState.UserInput import UserInput
from MouseInterfaces.Hoverable import Hoverable
import pygame, colors, graphics, Utility

# Edges are not draggable. even curved edges are completely determined by node positions and starting theta
class Edge(Hoverable, ABC):
    def __init__(self):
        super().__init__()
        self.beforePos: PointRef = None
        self.afterPos: PointRef = None

    @abstractmethod
    def compute(self, beforeHeading: float) -> float:
        pass

    @abstractmethod
    def drawHovered(self, screen: pygame.Surface):
        pass

    @abstractmethod
    def draw(screen: pygame.Surface):
        pass

# linear
class StraightEdge(Edge):
    def __init__(self):
        super().__init__()
        self.distance: float = None

    def compute(self, beforeHeading: float, beforePos: PointRef, afterPos: PointRef) -> float:
        self.heading = beforeHeading
        self.beforePos = beforePos
        self.afterPos = afterPos
        return self.heading

    # Check whether mouse is near the segment using a little math
    def checkIfHovering(self, userInput: UserInput) -> bool:
        a = self.beforePos.screenRef
        b = self.afterPos.screenRef
        return Utility.pointTouchingLine(*userInput.mousePosition.screenRef, *a, *b, 10)

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.GREEN, *self.beforePos.screenRef, self.heading)

    def draw(self, screen: pygame.Surface):
        # draw line between self.startPos and self.endPos
        if self.isHovering:
            color = colors.DARKBLUE
            thick = 4
        else:
            color = colors.BLACK
            thick = 3
        graphics.drawLine(screen, color, *self.beforePos.screenRef, *self.afterPos.screenRef, thick)


# circular arc
class CurveEdge(Edge):
    def __init__(self):
        super().__init__()
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