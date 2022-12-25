from Commands.AbstractCommand import Command
from Commands.NullCommand import NullCommand
from Commands.StartCommand import StartCommand
from Commands.ForwardCommand import ForwardCommand
from Commands.TurnCommand import TurnCommand

from Commands.Pose import Pose
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.SoftwareState import SoftwareState
import pygame, Utility
from typing import Iterator

"""
Stores a list of commands, which make up the path
"""

class Program:

    def __init__(self):

        self.commands: list[Command] = [ StartCommand(self) ]

    # append goTurnU() to the program
    def addTurn(self, absoluteHeading: float):
        if type(self.commands[-1]) == NullCommand:
            del self.commands[-1]
        
        self.commands[-1].next = TurnCommand(self, absoluteHeading)
        self.commands.append(self.commands[-1].next)
        self.commands[-1].previous = self.commands[-2]
        self.recompute()

    # append goForwardU() to the program
    def addForward(self, distanceInches: float):
        self.commands[-1].next = ForwardCommand(self, distanceInches)
        self.commands.append(self.commands[-1].next)
        self.commands[-1].previous = self.commands[-2]

        self.commands[-1].next = NullCommand(self)
        self.commands.append(self.commands[-1].next)
        self.commands[-1].previous = self.commands[-2]
        self.recompute()

    # User just clicked a point. Add a goForward there. But, if robot is not aimed towards
    # that point exactly, insert a turn beforehand
    def addPoint(self, targetPosition: PointRef):
        
        # get the robot's ending pose for the current path
        lastPose: Pose = self.commands[-1].afterPose

        # Calculate necessary heading to aim at target point
        headingToTarget = Utility.thetaTwoPoints(lastPose.pos.fieldRef, targetPosition.fieldRef)

        # If robot isn't aimed there already, add a point turn to that target heading
        if headingToTarget != lastPose.theta:

            # If it's the first command, just modify the start pose instead
            if len(self.commands) == 1:
                startCommand: StartCommand = self.commands[0]
                startCommand.setHeading(headingToTarget)
            else:
                # otherwise, just do the point turn
                self.addTurn(headingToTarget)


        # Add a goForwardU() command based on distance to target point
        distance = Utility.distanceTuples(lastPose.pos.fieldRef, targetPosition.fieldRef)
        self.addForward(distance)

    # Recompute the entire path given list of commands
    # Should be called whenever the path is modified
    def recompute(self):

        currentPose: Pose = None
        for command in self.commands:
            currentPose = command.compute(currentPose)

    # Draw entire path. Draw the segments under the icons
    def draw(self, screen: pygame.Surface, state: SoftwareState):

        # Draw the segments first
        for command in self.commands:
            if type(command) == ForwardCommand:
                command.draw(screen, command == state.objectSelected)

        # Draw the non-segments last
        for command in self.commands:
            if type(command) != ForwardCommand:
                command.draw(screen, command == state.objectSelected)    

    # Return the entire list of c++ instructions as a multiline string
    def getCode(self) -> str:
        string = ""
        for command in self.commands:
            code = command.getCode()
            if code is not None:
                string += code + "\n"

        return string

    # Get the list of commands that are hoverable for mouse interaction purposes
    def getHoverables(self) -> Iterator[Hoverable]:

        # First check for StartCommand and TurnCommand icons
        yield self.commands[0]
        for command in self.commands[1:]:
            if type(command) == TurnCommand:
                yield command

        # Then check for segments and curves
        for command in self.commands[1:]:
            if isinstance(command, Hoverable) and type(command) != TurnCommand:
                yield command