from Commands.Edge import Edge, StraightEdge, CurveEdge
from Commands.Node import *
from Commands.StartNode import StartNode
from Commands.TurnNode import TurnNode
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

        # linked list of nodes and edges. First element is the start node
        self.first: Node = StartNode(self)
        self.last: Node = self.first
        
        self.recompute()
        
    # add a edge and node to self.last, and then point to the new last node
    # Segment should be straight
    def addNodeForward(self, position: PointRef):
        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.last.next = StraightEdge(self, previous = self.last)
        self.recompute()

    # Segment should be curved with constraint with beforeHeading fixed
    def addNodeCurve(self, position: PointRef):

        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.last.next = StraightEdge(self, previous = self.last)
        self.recompute()

    
    def snapNewPoint(self, position: PointRef, node: Node = None) -> PointRef:
        # TODO
        return position.copy()

    # split edge into two and insert node into linked list where original edge was
    def insertNode(self, edge: StraightEdge, position: PointRef):
        
        # add another edge after the original one
        edge.next.previous = StraightEdge(next = edge.next)
        
        # Insert the node between the two edges
        edge.next = TurnNode(self, position, previous = edge, next = edge.next)

        self.recompute()

    # Delete a node and merge the two adjacent edges
    # We keep node.previous and delete node.next
    def deleteNode(self, node: TurnNode):
        
        # previous segment's next set to the node after next segment
        node.previous.next = node.next.next 

        # node after next segment's previous set to previous segment
        node.next.next.previous = node.previous

        # node parameter should be dereferenced after function scope ends

        self.recompute()

    # recalculate all the state for each point/edge and command after the list of points is modified
    def recomputePath(self):

        # only 1 node. return
        edge = self.first.next
        if edge is None:
            return
        
        # Compute all the edges first to update beforeHeading and afterHeading for each node
        edge.compute()
        while edge.next is not None:
            edge = edge.next.next
            edge.compute()

        # Compute all the nodes based on the heading values of the edges
        node = self.first
        node.compute()
        while node.next is not None:
            node = node.next.next
            node.compute()

        # Since the number of edges or nodes may have changed, or a turn was added/removed, update commands
        self.recomputeCommands()

    def recomputeCommands(self):

        # recompute commands
        x = Utility.SCREEN_SIZE + 17
        y = 18
        dy = 70
        for command in self.getHoverablesCommands():
            command.updatePosition(x, y)
            y += dy

    def getHoverablesPath(self, drawCurvePoints: bool = False) -> Iterator[Hoverable]:

        # Yield nodes first
        node = self.first
        yield node
        while node.next is not None:
            node = node.next.next
            yield node
        
        # Yield edges next
        edge = self.first.next
        if edge is not None:
            if drawCurvePoints:
                yield node
        while edge.next is not None:
            edge = edge.next.next
            if drawCurvePoints:
                yield edge.curve # Yield curve points if on ADD_CURVE mode
            yield edge

        return
        yield

    # Skip start node. Skip any nodes that don't turn
    def getHoverablesCommands(self) -> Iterator[Command]:

        current = self.first
        while current is not None:

            # as long as it's not a turn node without a turn, yield the command
            if not (type(current) == TurnNode and not current.hasTurn):
                yield current.command

            current = current.next

        return
        yield

    def drawPath(self, screen: pygame.Surface, drawCurvePoints: bool):

        # Draw the edges first
        edge = self.first.next
        if edge is not None:
            edge.draw(screen, drawCurvePoints)
        while edge.next is not None:
            edge = edge.next.next
            edge.draw(screen, drawCurvePoints)

        # Draw the nodes next
        node = self.first
        node.draw(screen)
        while node.next is not None:
            node = node.next.next
            node.draw(screen)

    def drawCommands(self, screen: pygame.Surface):

        # Draw the commands
        for command in self.getHoverablesCommands():
            command.draw(screen)

