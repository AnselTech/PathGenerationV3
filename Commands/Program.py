from Commands.Edge import Edge, StraightEdge
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
        self.last.next = StraightEdge(self, previous = self.last)
        self.last = self.last.next
        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.recompute()

    # Segment should be curved with constraint with beforeHeading fixed
    def addNodeCurve(self, position: PointRef):

        self.last.next = StraightEdge(self, previous = self.last)
        self.last = self.last.next
        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.recompute()

    
    def snapNewPoint(self, position: PointRef, node: Node = None) -> PointRef:
        # TODO
        return position.copy()

    # split edge into two and insert node into linked list where original edge was
    def insertNode(self, edge: StraightEdge, position: PointRef):
        
        # add another edge after the original one
        edge.next.previous = StraightEdge(self, next = edge.next)
        newEdge: Edge = edge.next.previous
        
        # Insert the node between the two edges
        edge.next = TurnNode(self, position, previous = edge, next = edge.next.previous)
        newEdge.previous = edge.next

        self.recompute()

    
    def deleteNode(self, node: TurnNode):

        if node.next is None:
            # If this is the last node, dereference this and the segment before it
            node.previous.previous.next = None

        else:
            # Otherwise, delete the node and merge the two adjacent edges
            # We keep node.previous and delete node.next

            # previous segment's next set to the node after next segment
            node.previous.next = node.next.next 

            # node after next segment's previous set to previous segment
            node.next.next.previous = node.previous

        # node parameter should be dereferenced after function scope ends

        self.recompute()

    # recalculate all the state for each point/edge and command after the list of points is modified
    def recompute(self):

        # only 1 node. return
        edge = self.first.next
        if edge is None:
            self.first.compute()
            return
        
        # Compute all the edges first to update beforeHeading and afterHeading for each node
        
        while edge is not None:
            edge.compute()
            edge = edge.next.next

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
        while edge is not None:

            if drawCurvePoints:
                yield edge.curve
            yield edge

            edge = edge.next.next

        return
        yield

    # Skip start node. Skip any nodes that don't turn
    def getHoverablesCommands(self) -> Iterator[Command]:

        current = self.first
        while current is not None:

            # no command if the turn node has no turn
            if type(current) == TurnNode and current.direction == 0:
                pass
            elif type(current) == StartNode: # start node has no command
                pass
            else:
                yield current.command

            current = current.next

        return
        yield

    def drawPath(self, screen: pygame.Surface, drawCurvePoints: bool):

        # Draw the edges first
        edge = self.first.next
        while edge is not None:
            edge.draw(screen, drawCurvePoints)
            edge = edge.next.next

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

