from abc import ABC, abstractmethod
import pygame
from Commands.Pose import Pose

"""
An abstract command which is an instruction that can be translated to c++, as well
as manipulate the robot's pose in some way
"""

class Command(ABC):

    def __init__(self):
        self.beforePose: Pose = None
        self.afterPose: Pose = None

    # Draw the command on the path on the graph
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

    # Update beforePose and afterPose based on the nature of hte command
    # Also return afterPose after the update
    # SHOULD NOT MODIFY initialPose parameter
    @abstractmethod
    def compute(self, initialPose: Pose) -> Pose:
        pass

    # Return the command in c++ code string form
    # Return None if no actual code generated from this command
    @abstractmethod
    def getCode(self) -> str:
        pass