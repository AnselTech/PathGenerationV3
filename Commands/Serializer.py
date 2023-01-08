from dataclasses import dataclass
from typing import Tuple
from Commands.StartNode import StartNode
from Commands.TurnNode import TurnNode
from Commands.Edge import StraightEdge
from SingletonState.ReferenceFrame import PointRef, Ref

"""
Convert linked list of nodes and edges <==> serializable data

Store data as:
Starting position (x,y) in field reference frame -> [float, float]
List of Segment objects"""

@dataclass # information storing a segment and a node connected to it
class Segment:
    beforeHeading: float # of edge
    straightCommandToggle: bool
    straightCommandSlider: float
    curveCommandToggle: bool
    curveCommandSlider: float
    shootHeadingCorrection: float
    shootActive: bool
    afterPosition: Tuple[float, float] # field ref

# Serializable class representing all the data for the path
# startNode is the start of the entire path linked list
class State:
    def __init__(self, startNode: StartNode):
        self.startPosition: Tuple[float, float] = startNode.position.fieldRef
        self.path: list[Segment] = []

        while startNode.next is not None:
            self.addSegment(startNode.next)
            startNode = startNode.next.next

    # serialize the edge and the node attached to that edge as a Segment object
    def addSegment(self, edge: StraightEdge):

        node: TurnNode = edge.next

        self.path.append(Segment(
            edge.beforeHeading,
            edge.straightCommand.toggle.isTopActive,
            edge.straightCommand.slider.getValue(),
            edge.curveCommand.toggle.isTopActive,
            edge.curveCommand.slider.getValue(),
            node.shoot.headingCorrection,
            node.shoot.active,
            node.position.fieldRef
        ))

    # Build the entire linked list from the serialized state
    # After a state object is unpickled, call load() to update program
    def load(self, program) -> StartNode:
        
        program.first = StartNode(program, None, None)
        program.first.position.fieldRef = self.startPosition

        previousNode = program.first

        for segment in self.path:
            
            edge: StraightEdge = StraightEdge(program, previous = previousNode, heading1 = segment.beforeHeading)
            previousNode.next = edge

            edge.straightCommand.toggle.isTopActive = segment.straightCommandToggle
            edge.straightCommand.slider.setValue(segment.straightCommandSlider)
            edge.curveCommand.toggle.isTopActive = segment.curveCommandToggle
            edge.curveCommand.slider.setValue(segment.curveCommandSlider)

            position = PointRef(Ref.FIELD, segment.afterPosition)
            node: TurnNode = TurnNode(program, position, previous = edge)
            edge.next = node

            node.shoot.headingCorrection = segment.shootHeadingCorrection
            node.shoot.active = segment.shootActive

            previousNode = node

        program.last = previousNode # update the pointer to the last node
            