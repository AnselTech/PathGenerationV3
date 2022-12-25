from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
import math, pygame, graphics, colors, Utility

"""
A command to go forward in the current direction some relative distance
"""

class ForwardCommand(Command):

    def __init__(self, program, distanceInches: float):

        super().__init__(program)

        self.distance: float = distanceInches

        self.SEGMENT_THICKNESS = 3
        self.SEGMENT_THICKNESS_2 = 4
        self.SEGMENT_HITBOX_THICKNESS = 8

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.beforePose = initialPose
        
        xpos, ypos = self.beforePose.pos.fieldRef
        xpos += self.distance * math.cos(initialPose.theta)
        ypos += self.distance * math.sin(initialPose.theta)

        self.afterPose = Pose(PointRef(Ref.FIELD, (xpos, ypos)), initialPose.theta)

        self.heading = Utility.thetaTwoPoints(self.beforePose.pos.fieldRef, self.afterPose.pos.fieldRef)

        return self.afterPose

    # Check whether mouse is near the segment using a little math
    def checkIfHovering(self, userInput: UserInput) -> bool:
        a = self.beforePose.pos.screenRef
        b = self.afterPose.pos.screenRef
        return Utility.pointTouchingLine(*userInput.mousePosition.screenRef, *a, *b, self.SEGMENT_HITBOX_THICKNESS)

    # goForwardU(distance)
    def getCode(self) -> str:
        return f"goForwardU({self.distance});"

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.GREEN, *self.beforePose.pos.screenRef, self.heading)

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface, isSelected: bool):

        # draw line between self.startPos and self.endPos
        if isSelected:
            color = colors.BLUE
            thick = self.SEGMENT_THICKNESS_2
        elif self.isHovering:
            color = colors.DARKBLUE
            thick = self.SEGMENT_THICKNESS_2
        else:
            color = colors.BLACK
            thick = self.SEGMENT_THICKNESS
        graphics.drawLine(screen, color, *self.beforePose.pos.screenRef, *self.afterPose.pos.screenRef, thick)

    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):
        pass