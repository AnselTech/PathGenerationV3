from Commands.Edge import Edge, StraightEdge, CurveEdge
from Commands.Node import Node, StartNode, TurnNode
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
        self.nodes: list[Node] = [ StartNode(self) ]
        self.edges: list[Edge] = []
        self.recompute()
        
    def addNodeForward(self, position: PointRef):
        print("add node forward")
        self.nodes.append(TurnNode(self, position))
        self.edges.append(StraightEdge())
        self.recompute()

    def addNodeCurve(self, position: PointRef):

        self.nodes.append(TurnNode(self, position))
        self.edges.append(CurveEdge())
        self.recompute()

    def recompute(self):
        if len(self.nodes) == 0:
            return
        elif len(self.nodes) == 1:
            self.nodes[0].compute(None, None)
            return

        heading = self.nodes[0].compute(None, self.nodes[1].position)
        for i in range(len(self.edges)):
            heading = self.edges[i].compute(heading, self.nodes[i].position, self.nodes[i+1].position)
            heading = self.nodes[i+1].compute(self.nodes[i].position, None if i == len(self.edges)-1 else self.nodes[i+1].position)

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