from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
from Commands.ForwardCommand import ForwardCommand
import math, pygame, graphics, colors, Utility

"""
This command runs only at the start of the program. It sets the initial pose of the robot
"""

class StartCommand(Command):

    def __init__(self, program):

        super().__init__(program)
        
        self.rawImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)
        self.rawImage2 = graphics.getImage("Images/Buttons/PathButtons/start2.png", 0.1)

        self.afterPose = Pose(PointRef(Ref.FIELD, (24, 48)), 0)
        self.setHeading(0)

    def setHeading(self, heading):
        self.afterPose.theta = heading
        print(heading * 180 / 3.1415)
        self.rotatedImage = pygame.transform.rotate(self.rawImage, heading * 180 / 3.1415)
        self.rotatedImage2 = pygame.transform.rotate(self.rawImage2, heading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    # Return the stored initial position of the robot to start the program
    def compute(self, initialPose: Pose) -> Pose:
        return self.afterPose

    # No code associated with this command
    def getCode(self) -> str:
        return None

    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.afterPose.pos.screenRef, userInput.mousePosition.screenRef)
        return distance < 20

    def drawHovered(self, screen: pygame.Surface):
        graphics.drawGuideLine(screen, colors.GREEN, *self.afterPose.pos.screenRef, self.afterPose.theta)

    # Draw the command on the path on the graph
    def draw(self, screen: pygame.Surface, isSelected: bool):
        if isSelected:
            image = self.rotatedImage2
        elif self.isHovering:
            image = self.rotatedImageH
        else:
            image = self.rotatedImage
        graphics.drawSurface(screen, image, *self.afterPose.pos.screenRef)

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
        self.afterPose.pos = userInput.mousePosition.copy()
        
        if self.next is not None and type(self.next) == ForwardCommand:
            forward: ForwardCommand = self.next
            forward.distance = Utility.distanceTuples(newPos, forward.afterPose.pos.fieldRef)
            self.setHeading(Utility.thetaTwoPoints(newPos, forward.afterPose.pos.fieldRef))

        self.program.recompute()