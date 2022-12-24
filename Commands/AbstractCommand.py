from abc import ABC, abstractmethod
import pygame
from Pose import Pose

class Command(ABC):

    # Draw the command on the path on the graph
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

    # Recompute the command's actions given the starting pose
    # Also return the modified pose after the command is run
    @abstractmethod
    def run(self, initialPose: Pose) -> Pose:
        pass

    # Return the command in c++ code string form
    @abstractmethod
    def getCode(self) -> str:
        pass