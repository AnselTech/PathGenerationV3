from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef
from MouseInterfaces.Hoverable import Hoverable
import pygame

# Edges are not draggable. even curved edges are completely determined by node positions and starting theta
class Edge(Hoverable, ABC):
    def __init__(self):
        self.beforePos: PointRef = None
        self.afaterPos: PointRef = None

    @abstractmethod
    def draw(screen: pygame.Surface):
        pass

# linear
class StraightEdge(Edge):
    def __init__(self):
        super().__init__()
        self.distance: float = None

# circular arc
class CurveEdge(Edge):
    def __init__(self):
        super().__init__()
        self.beforeHeading = None
        self.afterHeading = None
        
    # Given before and after positions, as well as before heading, update afterHeading based on circular arc
    def computeAfterHeading(self):
        #TODO
        pass