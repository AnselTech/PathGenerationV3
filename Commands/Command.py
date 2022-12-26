from abc import ABC, abstractmethod
from Sliders.Slider import Slider
import pygame
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput

class Command(Hoverable, ABC):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = None
        self.y = None

    def updatePosition(self, x, y):
        self.x = x
        self.y = y

    def checkIfHovering(self, userInput: UserInput) -> bool:
        x,y = userInput.mousePosition.screenRef
        if x < self.x or x > self.x + self.width:
            return False
        if y < self.y or y > self.y + self.height:
            return False
        return True

    def draw(self, screen: pygame.Surface, x, y):
        pass

class TurnCommand(Command):
    pass

class ForwardCommand(Command):
    pass

class CurveCommand(Command):
    pass

class ShootCommand(Command):
    pass