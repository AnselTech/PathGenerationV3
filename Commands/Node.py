from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
import pygame, graphics, Utility, colors, math

startImage = None
turnCImage = None
turnCCImage = None
turnCImageH = None
turnCCImageH = None
def init():
    global startImage, turnCImage, turnCCImage, turnCImageH, turnCCImageH
    startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)
    turnCImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
    turnCCImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
    turnCImageH = graphics.getLighterImage(turnCImage, 0.8)
    turnCCImageH = graphics.getLighterImage(turnCCImage, 0.8)

class Node(Draggable, ABC):

    def __init__(self, program, position: PointRef, hoverRadius: int):

        super().__init__()

        self.program = program
        self.position: PointRef = position.copy()
        self.hoverRadius = hoverRadius

        self.beforeHeading: float = None
        self.afterHeading: float = None


    # Called to determine if the mouse is touching this object (and if is the first object touched, would be considered hovered)
    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.position.screenRef, userInput.mousePosition.screenRef)
        return distance < self.hoverRadius

    # Callback when the dragged object was just released
    def stopDragging(self):
        pass

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass

    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):
        self.position = userInput.mousePosition.copy()
        self.program.recompute()

    def compute(self, beforePosition: PointRef, afterPosition: PointRef) -> float:
        if beforePosition is None:
            self.beforeHeading = None
        else:
            self.beforeHeading = Utility.thetaTwoPoints(beforePosition.fieldRef, self.position.fieldRef)

        if afterPosition is None:
            self.afterHeading = None
        else:
            self.afterHeading = Utility.thetaTwoPoints(self.position.fieldRef, afterPosition.fieldRef)

        self.computeSubclass()

        return self.afterHeading

    def computeSubclass(self):
        pass

    def drawHovered(self, screen: pygame.Surface):
        if self.afterHeading is not None:
            graphics.drawGuideLine(screen, colors.GREEN, *self.position.screenRef, self.afterHeading)

        if self.beforeHeading is not None:
            graphics.drawGuideLine(screen, colors.RED, *self.position.screenRef, self.beforeHeading)


    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

class StartNode(Node):

    def __init__(self, program):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(program, defaultStartPosition, 20)
        self.afterHeading = 0

    def computeSubclass(self):
        if self.afterHeading is None:
            self.rotatedImage = startImage
        else:
            self.rotatedImage = pygame.transform.rotate(startImage, self.afterHeading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface): 
        image = self.rotatedImageH if self.isHovering else self.rotatedImage
        graphics.drawSurface(screen, image, *self.position.screenRef)

class TurnNode(Node):

    def __init__(self, program, position: PointRef):

        super().__init__(program, position, 15)
        self.clockwise: bool = False
        self.hasTurn: bool = False
        self.afterHeading = 0

    # Given previous heading, return the resultant heading after the turn
    def computeSubclass(self) -> float:
        if self.afterHeading is None or math.isclose(self.beforeHeading, self.afterHeading):
            self.hasTurn = False
        else:
            self.hasTurn = True
            self.clockwise = Utility.deltaInHeading(self.afterHeading, self.beforeHeading) < 0

    def draw(self, screen: pygame.Surface): 
        # draw turn node
        if self.hasTurn:

            if self.clockwise:
                image = turnCImageH if self.isHovering else turnCImage
            else:
                image = turnCCImageH if self.isHovering else turnCCImage

            graphics.drawSurface(screen, image, *self.position.screenRef)

        else:
            # draw black node
            graphics.drawCircle(screen, *self.position.screenRef, colors.BLACK, 7 if self.isHovering else 5)