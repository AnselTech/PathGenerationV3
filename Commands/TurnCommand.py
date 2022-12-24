from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from SingletonState.ReferenceFrame import PointRef
import math, pygame, graphics, colors, Utility

"""
A command to perform a point turn in place to an absolute heading
"""

class TurnCommand(Command):

    def __init__(self, theta: float):

        super().__init__()

        self.heading: float = theta
        self.headingDegrees = theta * 180 / 3.1415
        self.clockwise: bool = False

        self.cImage = graphics.getImage("Images/Buttons/clockwise.png", 0.07)
        self.ccImage = graphics.getImage("Images/Buttons/counterclockwise.png", 0.07)

    # Go forward the direction the robot is already facing
    # save those two positions into the object to be drawn
    def compute(self, initialPose: Pose) -> Pose:

        self.beforePose = initialPose
        self.clockwise = Utility.deltaInHeading(self.heading, initialPose.theta)

        self.afterPose = Pose(initialPose.pos, self.heading)
        return self.afterPose

    # goTurnU(getRadians(headingDegrees))
    def getCode(self) -> str:
        return f"goTurnU(getRadians({self.headingDegrees}));"

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface):

        graphics.drawSurface(screen, self.cImage if self.clockwise else self.ccImage, *self.afterPose.pos.screenRef)