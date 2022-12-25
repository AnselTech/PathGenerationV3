from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from Commands.ForwardCommand import ForwardCommand
from Commands.StartCommand import StartCommand
from SingletonState.ReferenceFrame import PointRef
from SingletonState.UserInput import UserInput
import math, pygame, graphics, colors, Utility

"""
A command to perform a point turn in place to an absolute heading
"""

class TurnCommand(Command):

    def __init__(self, program, theta: float):

        super().__init__(program)

        self.heading: float = theta
        self.clockwise: bool = False

        self.cImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
        self.ccImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
        self.cImage2 = graphics.getImage("Images/Buttons/PathButtons/clockwise2.png", 0.07)
        self.ccImage2 = graphics.getImage("Images/Buttons/PathButtons/counterclockwise2.png", 0.07)
        self.cImageH = graphics.getLighterImage(self.cImage, 0.8)
        self.ccImageH = graphics.getLighterImage(self.ccImage, 0.8)


    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.beforePose = initialPose
        self.clockwise = Utility.deltaInHeading(self.heading, initialPose.theta) < 0

        self.afterPose = Pose(initialPose.pos, self.heading)
        self.previousHeading = Utility.thetaTwoPoints(self.previous.beforePose.pos.fieldRef, initialPose.pos.fieldRef)
        return self.afterPose

    # goTurnU(getRadians(headingDegrees))
    def getCode(self) -> str:
        return f"goTurnU(getRadians({self.heading * 180 / 3.1415}));"

    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.afterPose.pos.screenRef, userInput.mousePosition.screenRef)
        return distance < 20

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.RED, *self.beforePose.pos.screenRef, self.previousHeading)
        graphics.drawGuideLine(screen, colors.GREEN, *self.beforePose.pos.screenRef, self.heading)

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface, isSelected: bool):
        if isSelected:
            image = self.cImage2 if self.clockwise else self.ccImage2
        elif self.isHovering:
            image = self.cImageH if self.clockwise else self.ccImageH
        else:
            image = self.cImage if self.clockwise else self.ccImage

        graphics.drawSurface(screen, image, *self.afterPose.pos.screenRef)
            


    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        print("start")

    # Drag the turn node. This will affect many things:
    #    the distance of goForwardU to and from this node
    #    the angle of goTurnU for the previous turn, and as well as this current turn
    def beDraggedByMouse(self, userInput: UserInput):
        
        newPos = userInput.mousePosition.fieldRef

        if self.next is not None and type(self.next) == ForwardCommand:
            forward: ForwardCommand = self.next
            forward.distance = Utility.distanceTuples(newPos, forward.afterPose.pos.fieldRef)
            self.heading = Utility.thetaTwoPoints(newPos, forward.afterPose.pos.fieldRef)
        
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