from Commands.Edge import Edge, StraightEdge, CurveEdge
from Commands.Node import Node, StartNode, TurnNode
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.SoftwareState import SoftwareState, Mode
import pygame, Utility, math
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

    def snapNewPoint(self, position: PointRef, node: Node = None) -> PointRef:
        if node is None:
            i = len(self.nodes)
        else:
            i = self.nodes.index(node)

        if i >= 2:
            before: 'Node' = self.nodes[i-1]
            currentHeading = Utility.thetaTwoPoints(before.position.fieldRef, position.fieldRef)

            if abs(Utility.deltaInHeading(currentHeading, before.beforeHeading)) < 0.06:
                dist = Utility.distanceTuples(before.position.fieldRef, position.fieldRef)
                x = before.position.fieldRef[0] + dist * math.cos(before.beforeHeading)
                y = before.position.fieldRef[1] + dist * math.sin(before.beforeHeading)
                return PointRef(Ref.FIELD, (x,y))

        return position.copy()

    def deleteNode(self, node: TurnNode):
        
        # Last node. just delete last segment and node
        if node.afterHeading is None:
            del self.nodes[-1]
            del self.edges[-1]
        else:
            # connect the previous and next node together
            i = self.nodes.index(node)
            del self.nodes[i]
            del self.edges[i]

        self.recompute()

    # recalculate all the state for each point/edge and command after the list of points is modified
    def recompute(self):
        if len(self.nodes) == 0:
            return
        elif len(self.nodes) == 1:
            self.nodes[0].compute(None, None)
            return

        heading = self.nodes[0].compute(None, self.nodes[1])
        for i in range(len(self.edges)):
            heading = self.edges[i].compute(heading, self.nodes[i].position, self.nodes[i+1].position)
            heading = self.nodes[i+1].compute(self.nodes[i], None if i == len(self.edges)-1 else self.nodes[i+2])

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