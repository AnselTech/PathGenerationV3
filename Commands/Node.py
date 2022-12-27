from abc import ABC, abstractmethod
from SingletonState.ReferenceFrame import PointRef, Ref
from SingletonState.UserInput import UserInput
from MouseInterfaces.Draggable import Draggable
import pygame, graphics, Utility, colors, math
from Commands.Command import Command, TurnCommand

class Node(Draggable, ABC):

    def __init__(self, program, position: PointRef, hoverRadius: int):

        super().__init__()

        self.program = program
        self.position: PointRef = position.copy()
        self.hoverRadius = hoverRadius

        self.beforeHeading: float = None
        self.afterHeading: float = None

        self.command: Command = TurnCommand()


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

        self.position = self.program.snapNewPoint(userInput.mousePosition, self)
        self.program.recompute()

    def compute(self, before: 'Node', after: 'Node') -> float:


        if before is None:
            self.beforeHeading = None
        else:
            self.beforeHeading = Utility.thetaTwoPoints(before.position.fieldRef, self.position.fieldRef)
            
        if after is None:
            self.afterHeading = None
        else:
            self.afterHeading = Utility.thetaTwoPoints(self.position.fieldRef, after.position.fieldRef)
        
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