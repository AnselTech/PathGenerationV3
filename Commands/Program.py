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

    def delete(self, command: Command):
        if type(command) == StartCommand:
            return

        # delete both the null command and the movement before it
        if type(command) == NullCommand:
            command = command.previous
            command.next = None
            del self.commands[-1]

        if type(command) == ForwardCommand:
            # easy case, just delete end
            if command.next is None:
                command.previous.next = None
                del self.commands[-1]
            else:
                # not allowed to delete segments connected on both ends
                pass
        
        if type(command) == TurnCommand:
            # easy case, just delete end
            if command.next is None:
                print("deleete last turn")
                null = NullCommand(self)
                null.previous = command.previous
                command.previous.next = null
                print(self.commands[-1])
                del self.commands[-1]
                print(self.commands[-1].next)
                self.commands.append(null)
                print(self.commands)

            else:
                # join the previous and next goForwards together
                turn: TurnCommand = command
                forwardBefore: ForwardCommand = turn.previous
                forwardAfter: ForwardCommand = turn.next
                print("both", forwardBefore, forwardAfter)
                fro = forwardBefore.beforePose.pos.fieldRef
                to = forwardAfter.afterPose.pos.fieldRef
                forwardBefore.distance = Utility.distanceTuples(fro, to)
                forwardBefore.next = turn.next
                turn.next.previous = forwardBefore
                i = self.commands.index(turn)
                print(i)
                print(self.commands)
                print(len(self.commands))
                del self.commands[i+1]

                prevTurn: TurnCommand = forwardBefore.previous
                prevTurn.heading = Utility.thetaTwoPoints(fro, to)

        if len(self.commands) > 2 and type(self.commands[-1]) == NullCommand and type(self.commands[-2]) == TurnCommand:
            print("delete last null")
            del self.commands[-1]
            self.commands[-1].next = None

        self.recompute()



    # Recompute the entire path given list of commands
    # Should be called whenever the path is modified
    def recompute(self):

        currentPose: Pose = None
        for command in self.commands:
            currentPose = command.compute(currentPose)

        for i in range(len(self.commands)):
            if i != 0:
                assert(self.commands[i].previous is not None)
            if i != len(self.commands) - 1:
                assert(self.commands[i].next is not None)

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
            if type(command) != ForwardCommand:
                yield command

        # Then check for segments and curves
        for command in self.commands[1:]:
            if isinstance(command, Hoverable) and type(command) == ForwardCommand:
                yield command