from AbstractCommand import Command
from Pose import Pose
from SingletonState.ReferenceFrame import PointRef
import math, pygame, graphics, colors, Utility

class TurnCommand(Command):

    def __init__(self, theta):
        self.heading: float = theta
        self.headingDegrees = theta * 180 / 3.1415
        self.clockwise: bool = False
        self.pos: PointRef = None
        self.cImage = graphics.getImage("Images/Buttons/clockwise.png", 0.1)
        self.ccImage = graphics.getImage("Images/Buttons/counterclockwise.png", 0.1)

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.pos = initialPose.pos
        self.clockwise = Utility.deltaInHeading(self.heading, initialPose.theta)

        return Pose(initialPose.pos, self.heading)

    # goTurnU(getRadians(headingDegrees))
    def getCode(self) -> str:
        return f"goTurnU(getRadians({self.headingDegrees}));"

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface):

        graphics.drawSurface(screen, self.cImage if self.clockwise else self.ccImage, *self.pos.screenRef)