from AbstractCommand import Command
from Pose import Pose
from SingletonState.ReferenceFrame import PointRef, Ref
import math, pygame, graphics, colors

class ForwardCommand(Command):

    def __init__(self, distanceInches):
        self.distance: float = distanceInches
        self.startPos: PointRef = None
        self.endPos: PointRef = None

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.startPos = initialPose.pos
        
        xpos, ypos = self.startPos.fieldRef
        xpos += self.distance * math.cos(initialPose.theta)
        ypos += self.distance * math.sin(initialPose.theta)

        self.endPos = PointRef(Ref.FIELD, (xpos, ypos))

        return Pose(self.endPos, initialPose.theta)

    # goForwardU(distance)
    def getCode(self) -> str:
        return f"goForwardU({self.distance});"

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface):

        # draw line between self.startPos and self.endPos
        graphics.drawLine(screen, colors.BLACK, *self.startPos.screenRef, *self.endPos.screenRef, 5)