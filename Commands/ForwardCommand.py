from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from SingletonState.ReferenceFrame import PointRef, Ref
import math, pygame, graphics, colors

"""
A command to go forward in the current direction some relative distance
"""

class ForwardCommand(Command):

    def __init__(self, distanceInches: float):

        super().__init__()

        self.distance: float = distanceInches

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.beforePose = initialPose
        
        xpos, ypos = self.beforePose.pos.fieldRef
        xpos += self.distance * math.cos(initialPose.theta)
        ypos += self.distance * math.sin(initialPose.theta)

        self.afterPose = Pose(PointRef(Ref.FIELD, (xpos, ypos)), initialPose.theta)

        return self.afterPose

    # goForwardU(distance)
    def getCode(self) -> str:
        return f"goForwardU({self.distance});"

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface):

        # draw line between self.startPos and self.endPos
        graphics.drawLine(screen, colors.BLACK, *self.beforePose.pos.screenRef, *self.afterPose.pos.screenRef, 2)