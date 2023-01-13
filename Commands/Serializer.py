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
    reversed: bool
    beforeHeading: float # of edge
    straightCommandToggle: int
    straightCommandSpeedSlider: float
    straightCommandTimeSlider: float
    curveCommandToggle: int
    curveCommandSlider: float
    shootHeadingCorrection: float
    shootActive: bool
    shootCommandSlider: float
    shootTurnCommandToggle: int
    turnCommandToggle: int
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
            edge.reversed,
            edge.beforeHeading,
            edge.straightCommand.toggle.activeOption,
            edge.straightCommand.speedSlider.getValue(),
            edge.straightCommand.timeSlider.getValue(),
            edge.curveCommand.toggle.activeOption,
            edge.curveCommand.slider.getValue(),
            node.shoot.headingCorrection,
            node.shoot.active,
            node.shoot.shootCommand.slider.getValue(),
            node.shoot.turnToShootCommand.toggle.activeOption,
            node.command.toggle.activeOption,
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

            edge.reversed = segment.reversed
            edge.straightCommand.toggle.activeOption = segment.straightCommandToggle
            edge.straightCommand.speedSlider.setValue(segment.straightCommandSpeedSlider, disableCallback = True)
            edge.straightCommand.timeSlider.setValue(segment.straightCommandTimeSlider, disableCallback = True)
            edge.straightCommand.speedSlider.dy = -edge.straightCommand.DELTA_SLIDER_Y if (segment.straightCommandToggle == 3) else 0
            
            edge.curveCommand.toggle.activeOption = segment.curveCommandToggle
            edge.curveCommand.slider.setValue(segment.curveCommandSlider, disableCallback = True)

            position = PointRef(Ref.FIELD, segment.afterPosition)
            node: TurnNode = TurnNode(program, position, previous = edge)
            edge.next = node

            node.shoot.headingCorrection = segment.shootHeadingCorrection
            node.shoot.active = segment.shootActive
            node.shoot.turnToShootCommand.toggle.activeOption = segment.shootTurnCommandToggle
            node.shoot.shootCommand.slider.setValue(segment.shootCommandSlider, disableCallback = True)
            node.command.toggle.activeOption = segment.turnCommandToggle

            previousNode = node

        program.last = previousNode # update the pointer to the last node
        program.recompute()
            