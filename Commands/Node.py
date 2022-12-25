from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
import pygame, graphics, Utility, colors

class Node(Draggable, ABC):

    def __init__(self, position: PointRef, hoverRadius: int):
        self.position: PointRef = position
        self.hoverRadius = hoverRadius

        self.beforeHeading: float = None
        self.afterHeading: float = None


    # Called to determine if the mouse is touching this object (and if is the first object touched, would be considered hovered)
    def checkIfHovering(self, userInput: UserInput) -> bool:
        distance = Utility.distanceTuples(self.position.fieldRef, userInput.mousePosition.screenRef)
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
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

startImage = graphics.getImage("Images/Buttons/PathButtons/start.png", 0.1)
class StartNode(Node):

    def __init__(self):

        defaultStartPosition: PointRef = PointRef(Ref.FIELD, (24, 48))
        super().__init__(defaultStartPosition, 20)
        self.setHeading(0)

    def setHeading(self, heading):
        self.afterHeading = heading
        self.rotatedImage = pygame.transform.rotate(startImage, heading * 180 / 3.1415)
        self.rotatedImageH = graphics.getLighterImage(self.rotatedImage, 0.8)

    def draw(self, screen: pygame.Surface): 
        image = self.rotatedImageH if self.isHovering else self.rotatedImage
        screen.blit(image)

turnCImage = graphics.getImage("Images/Buttons/PathButtons/clockwise.png", 0.07)
turnCCImage = graphics.getImage("Images/Buttons/PathButtons/counterclockwise.png", 0.07)
turnCImageH = graphics.getLighterImage(turnCImage, 0.8)
turnCCImageH = graphics.getLighterImage(turnCCImage, 0.8)
class TurnNode(Node):

    def __init__(self, position: PointRef):

        super().__init__(position, 15)
        self.clockwise: bool = False
        self.hasTurn: bool = False

    # Given previous heading, return the resultant heading after the turn
    def compute(self, beforeHeading: float) -> float:
        self.beforeHeading = beforeHeading
        self.clockwise = Utility.deltaInHeading(self.afterHeading, beforeHeading) < 0
        return self.afterHeading

    def draw(self, screen: pygame.Surface): 
        # draw turn node
        if self.hasTurn:

            if self.clockwise:
                image = turnCImageH if self.isHovering else turnCImage
            else:
                image = turnCCImageH if self.isHovering else turnCCImage

            screen.blit(image)

        else:
            # draw black node
            graphics.drawCircle(screen, *self.position.screenRef, colors.BLACK, 7 if self.isHovering else 5)