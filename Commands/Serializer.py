from dataclasses import dataclass
from typing import Tuple
from Commands.StartNode import StartNode
from Commands.TurnNode import TurnNode
from Commands.Edge import StraightEdge
from Commands.CustomCommand import *
from SingletonState.ReferenceFrame import PointRef, Ref

"""
Convert linked list of nodes and edges <==> serializable data

Store data as:
Starting position (x,y) in field reference frame -> [float, float]
List of Segment objects"""

"""
id: code
info:
    code => [code string]

id: wait
info:
    time => [time in seconds]

id: intake
info:
    speed => [speed -1 to 1]

"""
@dataclass
class CustomCommandData: # not used for the regular commands (forward/turn/curve/shoot) because legacy code. only additional ones
    id: str # custom, wait, intake, roller
    info: dict

def loadCustomState(program, data: CustomCommandData):
        if data.id == "code":
            return CodeCommand(program, text = data.info["code"])
        elif data.id == "time":
            return TimeCommand(program, time = data.info["time"])
        elif data.id == "intake":
            return IntakeCommand(program, intakeSpeed = data.info["speed"])
        else:
            raise Exception("Invalid command type.")

def saveCustomState(command: CustomCommand) -> CustomCommandData:
    if isinstance(command, CodeCommand):
        return CustomCommandData("code", {"code" : command.textbox.code})
    elif isinstance(command, TimeCommand):
        return CustomCommandData("time", {"time" : command.time})
    elif isinstance(command, IntakeCommand):
        return CustomCommandData("intake", {"speed" : command.slider.getValue()})
    else:
        raise Exception("Cannot serialize command: ", str(command))

@dataclass # information storing a segment and a node connected to it
class Segment:
    reversed: bool
    beforeHeading: float # of edge
    straightCommandToggle: int
    straightCommandSpeedSlider: float
    straightCommandTimeSlider: float
    straightCommandCustom: list[CustomCommandData]
    curveCommandToggle: int
    curveCommandSlider: float
    curveCommandCustom: list[CustomCommandData]
    shootHeadingCorrection: float
    shootActive: bool
    shootCommandSlider: float
    shootCommandCustom: list[CustomCommandData]
    shootTurnCommandToggle: int
    shootTurnCommandCustom: list[CustomCommandData]
    turnCommandToggle: int
    turnCommandCustom: list[CustomCommandData]
    afterPosition: Tuple[float, float] # field ref

# Serializable class representing all the data for the path
# startNode is the start of the entire path linked list
class State:
    def __init__(self, startNode: StartNode):
        self.startPosition: Tuple[float, float] = startNode.position.fieldRef
        self.startHeading = startNode.startHeading
        self.path: list[Segment] = []

        while startNode.next is not None:
            self.addSegment(startNode.next)
            startNode = startNode.next.next

    def getCustom(self, command: CustomCommand) -> list[CustomCommandData]:
        code: list[CustomCommandData] = []
        while command.nextCustomCommand is not None:
            command = command.nextCustomCommand
            code.append(saveCustomState(command))
        return code

    # serialize the edge and the node attached to that edge as a Segment object
    def addSegment(self, edge: StraightEdge):

        node: TurnNode = edge.next

        self.path.append(Segment(
            edge.reversed,
            edge.beforeHeading,
            edge.straightCommand.toggle.activeOption,
            edge.straightCommand.speedSlider.getValue(),
            edge.straightCommand.timeSlider.getValue(),
            self.getCustom(edge.straightCommand),
            edge.curveCommand.toggle.activeOption,
            edge.curveCommand.slider.getValue(),
            self.getCustom(edge.curveCommand),
            node.shoot.headingCorrection,
            node.shoot.active,
            node.shoot.shootCommand.slider.getValue(),
            self.getCustom(node.shoot.shootCommand),
            node.shoot.turnToShootCommand.toggle.activeOption,
            self.getCustom(node.shoot.turnToShootCommand),
            node.command.toggle.activeOption,
            self.getCustom(node.command),
            node.position.fieldRef
        ))

    def loadCustom(self, program, codes: list[CustomCommandData]) -> CustomCommand:

        if len(codes) == 0:
            return None

        first = loadCustomState(program, codes[0])

        previous: CustomCommand = first
        for code in codes[1:]:
            command = loadCustomState(program, code)
            previous.nextCustomCommand = command
            previous = command

        return first

    # Build the entire linked list from the serialized state
    # After a state object is unpickled, call load() to update program
    def load(self, program) -> StartNode:
        
        program.first = StartNode(program, None, None)
        program.first.position.fieldRef = self.startPosition
        program.first.startHeading = self.startHeading

        previousNode = program.first

        for segment in self.path:
            
            edge: StraightEdge = StraightEdge(program, previous = previousNode, heading1 = segment.beforeHeading)
            previousNode.next = edge

            edge.reversed = segment.reversed
            edge.straightCommand.toggle.activeOption = segment.straightCommandToggle
            edge.straightCommand.speedSlider.setValue(segment.straightCommandSpeedSlider, disableCallback = True)
            edge.straightCommand.timeSlider.setValue(segment.straightCommandTimeSlider, disableCallback = True)
            edge.straightCommand.speedSlider.dy = -edge.straightCommand.DELTA_SLIDER_Y if (segment.straightCommandToggle == 3) else 0
            edge.straightCommand.nextCustomCommand = self.loadCustom(program, segment.straightCommandCustom)

            edge.curveCommand.toggle.activeOption = segment.curveCommandToggle
            edge.curveCommand.slider.setValue(segment.curveCommandSlider, disableCallback = True)
            edge.curveCommand.nextCustomCommand = self.loadCustom(program, segment.curveCommandCustom)

            position = PointRef(Ref.FIELD, segment.afterPosition)
            node: TurnNode = TurnNode(program, position, previous = edge)
            edge.next = node

            node.shoot.headingCorrection = segment.shootHeadingCorrection
            node.shoot.active = segment.shootActive
            node.shoot.turnToShootCommand.toggle.activeOption = segment.shootTurnCommandToggle
            node.shoot.turnToShootCommand.nextCustomCommand = self.loadCustom(program, segment.shootTurnCommandCustom)
            node.shoot.shootCommand.slider.setValue(segment.shootCommandSlider, disableCallback = True)
            node.shoot.shootCommand.nextCustomCommand = self.loadCustom(program, segment.shootCommandCustom)
            node.command.toggle.activeOption = segment.turnCommandToggle
            node.command.nextCustomCommand = self.loadCustom(program, segment.turnCommandCustom)

            previousNode = node

        program.last = previousNode # update the pointer to the last node
        program.recompute()
            