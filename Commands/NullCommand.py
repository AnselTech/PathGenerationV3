from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from Commands.ForwardCommand import ForwardCommand
from Commands.StartCommand import StartCommand
from Commands.TurnCommand import TurnCommand
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
import math, pygame, graphics, colors, Utility

"""
A null/filler command to add a visual node between two commands (i.e between a goForward and a goCurve) or at the very end
"""

class NullCommand(Command):

    def __init__(self, program):

        super().__init__(program)

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.beforePose = initialPose
        self.afterPose = initialPose

        self.heading = Utility.thetaTwoPoints(self.previous.beforePose.pos.fieldRef, self.afterPose.pos.fieldRef)

        return initialPose

    # goForwardU(distance)
    def getCode(self) -> str:
        return None

    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.afterPose.pos.screenRef, userInput.mousePosition.screenRef)
        return distance < 12

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.GREEN, *self.beforePose.pos.screenRef, self.heading)

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface, isSelected: bool):
        if isSelected:
            color = colors.BLUE
        elif self.isHovering:
            color = colors.DARKBLUE
        else:
            color = colors.BLACK
        graphics.drawCircle(screen, *self.afterPose.pos.screenRef, color, 7 if self.isHovering else 5)

    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):
        newPos = userInput.mousePosition.fieldRef

        if self.previous is not None and type(self.previous) == ForwardCommand:
            forward: ForwardCommand = self.previous
            forward.distance = Utility.distanceTuples(forward.beforePose.pos.fieldRef, newPos)

            if forward.previous is not None and type(forward.previous) == TurnCommand:
                turn: TurnCommand = forward.previous
                turn.heading = Utility.thetaTwoPoints(forward.beforePose.pos.fieldRef, newPos)
            elif forward.previous is not None and type(forward.previous) == StartCommand:
                start: StartCommand = forward.previous
                start.setHeading(Utility.thetaTwoPoints(forward.beforePose.pos.fieldRef, newPos))

        self.program.recompute()