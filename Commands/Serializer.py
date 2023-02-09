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
    commented => bool

id: wait
info:
    time => [time in seconds]
    commented => bool

id: intake
info:
    speed => [speed -1 to 1]
    commented => bool

id: roller
info:
    speed => [speed -1 to 1]
    mode -> [0/1 for distance/time]
    distance => rotations in degrees
    time => seconds
    commented => bool

"""
@dataclass
class CustomCommandData: # not used for the regular commands (forward/turn/curve/shoot) because legacy code. only additional ones
    id: str # custom, wait, intake, roller
    info: dict

def loadCustomState(program, data: CustomCommandData):
        if data.id == "code":
            command =  CodeCommand(program, text = data.info["code"])
        elif data.id == "time":
            command =  TimeCommand(program, time = data.info["time"])
        elif data.id == "intake":
            command =  IntakeCommand(program, intakeSpeed = data.info["speed"])
        elif data.id == "roller":
            command = RollerCommand(program,
                rollerSpeed = data.info["speed"],
                toggleMode = data.info["mode"],
                rollerDistance = data.info["distance"],
                rollerTime = data.info["time"]
            )
        elif data.id == "backIntoRoller":
            command = DoRollerCommand(program)
        elif data.id == "flap":
            command = FlapCommand(program, flapUp = data.info["toggle"])
        else:
            raise Exception("Invalid command type.")

        try:
            command.commented = data.info["commented"]
        except:
            pass
    
        return command

def saveCustomState(command: CustomCommand) -> CustomCommandData:
    if isinstance(command, CodeCommand):
        return CustomCommandData("code", {
            "code" : command.textbox.code,
            "commented" : command.commented
        })
    elif isinstance(command, TimeCommand):
        return CustomCommandData("time", {
            "time" : command.time,
            "commented" : command.commented
        })
    elif isinstance(command, IntakeCommand):
        return CustomCommandData("intake", {
            "speed" : command.slider.getValue(),
            "commented" : command.commented,
        })
    elif isinstance(command, RollerCommand):
        dict = {
            "speed" : command.sliderSpeed.getValue(),
            "mode" : command.toggle.get(int),
            "distance" : command.sliderDistance.getValue(),
            "time" : command.sliderTime.getValue(),
            "commented" : command.commented
        }
        return CustomCommandData("roller", dict)
    elif isinstance(command, FlapCommand):
        return CustomCommandData("flap", {
            "toggle" : command.toggle.activeOption,
            "commented" : command.commented
        })
    elif isinstance(command, DoRollerCommand):
        return CustomCommandData("backIntoRoller", {
            "commented" : command.commented
        })
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
    straightCommandCommented: bool
    curveCommandToggle: int
    curveCommandSlider: float
    curveCommandCustom: list[CustomCommandData]
    curveCommandCommented: bool
    shootHeadingCorrection: float
    shootActive: bool
    shootCommandSlider: float
    shootCommandCustom: list[CustomCommandData]
    shootCommandCommented: bool
    shootTurnCommandToggle: int
    shootTurnCommandCustom: list[CustomCommandData]
    shootTurnCommandCommented: bool
    turnCommandToggle: int
    turnCommandCustom: list[CustomCommandData]
    turnCommandCommented: bool
    afterPosition: Tuple[float, float] # field ref

# Serializable class representing all the data for the path
# startNode is the start of the entire path linked list
class State:

    def getCustom(self, command: CustomCommand) -> list[CustomCommandData]:
        code: list[CustomCommandData] = []
        while command.nextCustomCommand is not None:
            command = command.nextCustomCommand
            code.append(saveCustomState(command))
        return code
    
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

    
    def __init__(self, startNode: StartNode, beforeStartCommand):
        self.startPosition: Tuple[float, float] = startNode.position.fieldRef
        self.startHeading = startNode.startHeading
        self.path: list[Segment] = []

        self.beforeStartCustom = self.getCustom(beforeStartCommand)

        # need to refactor properly v3.5
        self.startCommented = startNode.command.commented
        self.startCustom = self.getCustom(startNode.command)

        while startNode.next is not None:
            self.addSegment(startNode.next)
            startNode = startNode.next.next

    

    # serialize the edge and the node attached to that edge as a Segment object
    def addSegment(self, edge: StraightEdge):

        node: TurnNode = edge.next

        self.path.append(Segment(
            reversed = edge.reversed,
            beforeHeading = edge.beforeHeading,
            straightCommandToggle = edge.straightCommand.toggle.activeOption,
            straightCommandSpeedSlider = edge.straightCommand.speedSlider.getValue(),
            straightCommandTimeSlider = edge.straightCommand.timeSlider.getValue(),
            straightCommandCustom = self.getCustom(edge.straightCommand),
            straightCommandCommented = edge.straightCommand.commented,
            curveCommandToggle = edge.curveCommand.toggle.activeOption,
            curveCommandSlider = edge.curveCommand.slider.getValue(),
            curveCommandCustom = self.getCustom(edge.curveCommand),
            curveCommandCommented = edge.curveCommand.commented,
            shootHeadingCorrection = node.shoot.headingCorrection,
            shootActive = node.shoot.active,
            shootCommandSlider = node.shoot.shootCommand.slider.getValue(),
            shootCommandCustom = self.getCustom(node.shoot.shootCommand),
            shootCommandCommented = node.shoot.shootCommand.commented,
            shootTurnCommandToggle = node.shoot.turnToShootCommand.toggle.activeOption,
            shootTurnCommandCustom = self.getCustom(node.shoot.turnToShootCommand),
            shootTurnCommandCommented = node.shoot.turnToShootCommand.commented,
            turnCommandToggle = node.command.toggle.activeOption,
            turnCommandCustom = self.getCustom(node.command),
            turnCommandCommented = node.command.commented,
            afterPosition = node.position.fieldRef
        ))

    # Build the entire linked list from the serialized state
    # After a state object is unpickled, call load() to update program
    def load(self, program) -> StartNode:

        program.firstCommand.nextCustomCommand = self.loadCustom(program, self.beforeStartCustom)
        
        program.first = StartNode(program, None, None)
        program.first.position.fieldRef = self.startPosition
        program.first.startHeading = self.startHeading

        try:
            program.first.command.commented = self.startCommented
            program.first.command.nextCustomCommand = self.loadCustom(program, self.startCustom)
        except Exception as e:
            print("could not load custom commands after first turn command.")
            print(e)

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
            try:
                edge.straightCommand.commented = segment.straightCommandCommented
            except:
                pass

            edge.curveCommand.toggle.activeOption = segment.curveCommandToggle
            edge.curveCommand.slider.setValue(segment.curveCommandSlider, disableCallback = True)
            edge.curveCommand.nextCustomCommand = self.loadCustom(program, segment.curveCommandCustom)
            try:
                edge.curveCommand.commented = segment.curveCommandCommented
            except:
                pass


            position = PointRef(Ref.FIELD, segment.afterPosition)
            node: TurnNode = TurnNode(program, position, previous = edge)
            edge.next = node

            node.shoot.headingCorrection = segment.shootHeadingCorrection
            node.shoot.active = segment.shootActive

            node.shoot.turnToShootCommand.toggle.activeOption = segment.shootTurnCommandToggle
            node.shoot.turnToShootCommand.nextCustomCommand = self.loadCustom(program, segment.shootTurnCommandCustom)
            try:
                node.shoot.turnToShootCommand.commented = segment.shootTurnCommandCommented
            except:
                pass

            node.shoot.shootCommand.slider.setValue(segment.shootCommandSlider, disableCallback = True)
            node.shoot.shootCommand.nextCustomCommand = self.loadCustom(program, segment.shootCommandCustom)
            try:
                node.shoot.shootCommand.commented = segment.shootCommandCommented
            except:
                pass

            node.command.toggle.activeOption = segment.turnCommandToggle
            node.command.nextCustomCommand = self.loadCustom(program, segment.turnCommandCustom)
            try:
                node.command.commented = segment.turnCommandCommented
            except:
                pass

            previousNode = node

        program.last = previousNode # update the pointer to the last node
        program.recompute()
            