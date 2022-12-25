from Edge import Edge, StraightEdge, CurveEdge
from Node import Node, StartNode, TurnNode
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.SoftwareState import SoftwareState, Mode
import pygame, Utility
from typing import Iterator

"""
Stores a list of commands, which make up the path
"""

class Program:

    def __init__(self):
        self.nodes: list[Node] = [ StartNode() ]
        self.edges: list[Edge] = []
        
    def addNode(self, state: SoftwareState, position: PointRef):

        self.nodes.append(TurnNode(position))
        if state.mode == Mode.ADD_SEGMENT:
            newEdge = StraightEdge()
        else:
            newEdge = CurveEdge()
        self.edges.append(newEdge)

    def getHoverables(self) -> Iterator[Hoverable]:

        for node in self.nodes:
            yield node

        for edge in self.edges:
            yield edge

        return
        yield

    def draw(self, screen: pygame.Surface):
        for edge in self.edges:
            edge.draw(screen)
        for node in self.nodes:
            node.draw(screen)