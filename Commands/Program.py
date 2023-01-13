from Commands.Edge import Edge, StraightEdge
from Commands.Node import *
from Commands.StartNode import StartNode
from Commands.TurnNode import TurnNode
from Commands.Scroller import Scroller
from Commands.TextButton import TextButton
from Commands.Between import Between
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.ReferenceFrame import PointRef, Ref, VectorRef
from SingletonState.SoftwareState import SoftwareState, Mode
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from RobotImage import RobotImage
import pygame, Utility, math
from typing import Iterator
from timeit import default_timer as timer

"""
Stores a list of commands, which make up the path
"""

class Program:

    def __init__(self, state: SoftwareState):

        self.state = state

        # linked list of nodes and edges. First element is the start node
        self.first: Node = StartNode(self)
        self.last: Node = self.first

        self.scroller: Scroller = Scroller(self, Utility.SCREEN_SIZE + Utility.PANEL_WIDTH - 19, 10, 13, Utility.SCREEN_SIZE - 20)
        
        self.code: str = ""
        self.codeLines: list[str] = []

        self.betwens: list[Between] = []

        self.hoveredBetween = None

        self.recompute()
        self.recomputeGeneratedCode(None)
        
    # add a edge and node to self.last, and then point to the new last node
    # Segment should be straight
    def addNodeForward(self, position: PointRef):
        
        heading = Utility.thetaTwoPoints(self.last.position.fieldRef, position.fieldRef)
        self.last.next = StraightEdge(self, previous = self.last, heading1 = heading)
        self.last = self.last.next
        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.recompute()

    # Segment should be curved with constraint with beforeHeading fixed
    def addNodeCurve(self, position: PointRef):

        position, isStraight = self.snapNewPoint(position)
        if isStraight:
            self.addNodeForward(position)
            return

        if self.first is self.last:
            heading = 0
        else:
            heading = self.last.previous.afterHeading

        self.last.next = StraightEdge(self, previous = self.last, heading1 = heading)
        self.last = self.last.next
        self.last.next = TurnNode(self, position, previous = self.last)
        self.last = self.last.next
        self.recompute()

    # returns the adjusted position. true if straight, false if curve
    def snapNewPoint(self, position: PointRef) -> PointRef:
        # TODO

        if self.first is not self.last:
            previousHeading = self.last.previous.afterHeading
            currentHeading = Utility.thetaTwoPoints(self.last.position.fieldRef, position.fieldRef)
            if abs(previousHeading - currentHeading) < 0.12:
                distance = Utility.distanceTuples(self.last.position.fieldRef, position.fieldRef)
                return self.last.position + VectorRef(Ref.FIELD, magnitude = distance, heading = previousHeading), True

        return position.copy(), False

    # split edge into two and insert node into linked list where original edge was
    def insertNode(self, edge: StraightEdge, position: PointRef):
        
        # add another edge after the original one
        if edge.arc.isStraight:
            heading = edge.beforeHeading
        else:
            # calculate the heading that would result if the arc was unchanged with the new node's insertion
            dx = position.fieldRef[0] - edge.previous.position.fieldRef[0]
            dy = position.fieldRef[1] - edge.previous.position.fieldRef[1]
            heading = Utility.thetaFromArc(edge.beforeHeading, dx, dy)
        newEdge: Edge = StraightEdge(self, next = edge.next, heading1 = heading)
        edge.next.previous = newEdge
        
        # Insert the node between the two edges
        edge.next = TurnNode(self, position, previous = edge, next = newEdge)
        newEdge.previous = edge.next

        self.recompute()

    
    def deleteNode(self, node: TurnNode):

        if node.next is None:
            # If this is the last node, dereference this and the segment before it
            self.last = node.previous.previous
            self.last.next = None

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
            self.recomputeCommands()
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

        self.betweens: list[Between] = []

        # recompute commands
        x = Utility.SCREEN_SIZE + 14
        y = 18 - self.scroller.contentY
        dy = 74

        commands = list(self.getHoverablesCommands())
        contentHeight = len(commands) * dy
        self.scroller.update(contentHeight)

        for command in commands:
            command.updatePosition(x, y)
            y += dy

            if command is not commands[-1]: # if not last node
                self.betweens.append(Between(command, y - (dy-Command.COMMAND_HEIGHT)/2))

        self.recomputeGeneratedCode(commands)

    def recomputeGeneratedCode(self, commands: list[Command] = None):
        if commands is None:
            commands = list(self.getHoverablesCommands())

        if self.first.next is None:
            self.code = "// (Empty path. no code generated)"
            self.codeLines = []
            return

        def setFlywheelSpeedCommand(code, commands):
            for command in commands:
                if type(command) == ShootCommand:
                    speed = int(command.slider.getValue())
                    return code + f"robot.flywheel->setVelocity({speed}); // Preemptively set speed for next shot\n"
            return code

        x,y = self.first.position.fieldRef
        x = round(x, 1)
        y = round(y, 1)
        startHeading = round(self.first.startHeading * 180 / 3.1415, 2)
        
        code = "// GENERATED C++ CODE FROM PathGen 3.0\n\n"
        code += f"// Robot assumes a starting position of ({x},{y}) at heading of {startHeading} degrees.\n"
        code = setFlywheelSpeedCommand(code, commands)
        code += f"robot.localizer->setHeading(getRadians({startHeading}));\n\n"

        for i in range(len(commands)):
            command = commands[i]
            isShooter = type(command) == ShootCommand

            if isShooter:
                code += "\n"
            
            code += command.getCode() + "\n"

            if isShooter:
                code = setFlywheelSpeedCommand(code, commands[i+1:]) + "\n"

        self.code = code + "// ================================================\n"
        self.codeLines = self.code.split("\n")

    def getHoverablesPath(self, state: SoftwareState) -> Iterator[Hoverable]:

        # Yield nodes first
        node = self.first
        yield node
        while node.next is not None:
            node: Node = node.next.next
            yield node
            if node.shoot.active:
                yield node.shoot

        # Yield edge heading points next
        if not state.mode == Mode.MOUSE_SELECT and not state.mode == Mode.PLAYBACK:
            edge = self.first.next
            while edge is not None:
                yield edge.headingPoint
                edge = edge.next.next        
        
        # Yield edges next
        edge = self.first.next
        while edge is not None:
            yield edge
            edge = edge.next.next

        return
        yield

    # Skip start node. Skip any nodes that don't turn
    # Does not include custom commands
    def _getHoverablesCommands(self) -> Iterator[Command]:

        current = self.first
        while current is not None:

            # no command if the turn node has no turn
            if type(current) == TurnNode and current.shoot.active:
                if not Utility.headingsEqual(current.previous.goalHeading, current.shoot.heading):
                    yield current.shoot.turnToShootCommand
                yield current.shoot.shootCommand
                if current.next is not None and not Utility.headingsEqual(current.shoot.heading, current.goalHeading):
                    yield current.command
            elif type(current) == TurnNode and current.direction == 0:
                pass
            elif type(current) == StartNode: # start node has no command
                pass
            else:
                yield current.command

            current = current.next

        return
        yield

    # includes custom commands
    def getHoverablesCommands(self) -> Iterator[Command]:
        for command in self._getHoverablesCommands():
            yield command
            c = command.nextCustomCommand
            while c is not None:
                yield c
                c = c.nextCustomCommand
        return
        yield

    def getHoverablesOther(self):
        for between in self.betweens:
            yield between.plus
            yield between

        return
        yield

    def drawPath(self, screen: pygame.Surface, state: SoftwareState):

        # Draw the edges first
        edge = self.first.next
        while edge is not None:
            edge.draw(screen, not state.mode == Mode.MOUSE_SELECT and not state.mode == Mode.PLAYBACK)
            edge = edge.next.next

        # Draw the nodes next
        node = self.first
        node.draw(screen)
        while node.next is not None:
            node = node.next.next
            node.draw(screen)

    def drawCommands(self, screen: pygame.Surface):


        # Draw the commands
        if self.state.isCode:
            x = Utility.SCREEN_SIZE + 10
            y = 10
            for text in self.codeLines:
                graphics.drawText(screen, graphics.FONTCODE, text, colors.BLACK, x, y, 0, 0.5)
                y += 11
        else:

            self.scroller.draw(screen)

            for command in self.getHoverablesCommands():
                command.draw(screen)

            for between in self.betweens:
                between.draw(screen)

    def drawSimulation(self, screen: pygame.Surface, robotImage: RobotImage):

        if not self.state.mode == Mode.PLAYBACK:
            return

        # Update simulation tick
        if (timer() - self.previousTickTime) > Simulator.TIMESTEP:
            self.simulationTick += 1
            self.previousTickTime = timer()

            # If at the end of simulation list, end simulation
            if len(self.simulationList) == self.simulationTick:
                self.state.mode = self.modeBeforePlayback
                return

        # Draw the robot at the simulation state
        simulationState: SimulationState = self.simulationList[self.simulationTick]
        robotImage.draw(screen, simulationState.robotPosition, simulationState.robotHeading)

    # Return whether the simulation has actually been generated
    def generateSimulation(self) -> bool:

        self.simulationList: list[SimulationState] = []

        # handle base case of nonexistent path
        if self.first.next is None:
            return

        currentState: SimulationState = SimulationState(self.first.position, self.first.startHeading, 0, 0)
        simulator: Simulator = Simulator(currentState)
        self.simulationList.append(currentState)

        for command in self.getHoverablesCommands():

            command.initSimulationController(currentState)

            for i in range(200): # repeat while command is not finished, or 200 ticks reached (timeout)
                controllerInput: ControllerInputState = command.simulateTick(currentState)
                currentState = simulator.simulateTick(controllerInput)
                self.simulationList.append(currentState)

                # When command is finished, go onto the next
                if controllerInput.isDone:
                    break
            else:
                print("Command ended from timeout: ", command.getCode())
        
        # wait for robot to come to a complete stop in the simulation
        while Utility.hypo(simulator.xVelocity, simulator.yVelocity) > 0.05:
            currentState = simulator.simulateTick(ControllerInputState(0, 0, None))
            self.simulationList.append(currentState)

        self.previousTickTime = timer()
        self.simulationTick = 0
        self.modeBeforePlayback = self.state.mode
        self.state.mode = Mode.PLAYBACK

    # When custom command is dragged, find hovered between object to display it visually
    def dragCustomCommand(self, userInput: UserInput):
        self.hoveredBetween = None
        for between in self.betweens:
            if between.checkIfHovering(userInput, Command.COMMAND_HEIGHT):
                self.hoveredBetween = between
                return
        
    # very inefficient approach but oh well, don't want to refactor
    def _getPreviousCommand(self, targetCommand):
        previous = None
        for command in self.getHoverablesCommands():
            if command is targetCommand:
                return previous
            previous = command

    # Move Custom Command to between object where mouse was released
    def stopDragCustomCommand(self, command):

        if self.hoveredBetween is None or self.hoveredBetween.beforeCommand is command:
            self.hoveredBetween = None
            return

        # At this point, means that custom command was dragged into this between node

        # Remove command from current position
        previous = self._getPreviousCommand(command)
        previous.nextCustomCommand = command.nextCustomCommand

        before = self.hoveredBetween.beforeCommand # insert after this before command
        if before.nextCustomCommand is not None:
            command.nextCustomCommand = before.nextCustomCommand
        before.nextCustomCommand = command

        self.hoveredBetween = None

        self.recomputeCommands()