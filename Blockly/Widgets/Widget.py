from abc import ABC, abstractmethod
from MouseInterfaces.Hoverable import Hoverable
import pygame

def init(programObject):
    global program
    program = programObject

class Widget(Hoverable):

    def __init__(self):

        self.isVisible = True
        self.program = program

    # Called whenever parent command's position is moved. Recompute widget position
    @abstractmethod
    def updatePosition(self, x, y):
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass