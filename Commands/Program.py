from Commands.AbstractCommand import Command
from Commands.Pose import Pose
from SingletonState.ReferenceFrame import PointRef, Ref
import pygame

"""
Stores a list of commands, which make up the path
"""

defaultStartPose = Pose(PointRef(Ref.FIELD, (24, 48)), 0)

class Program:

    def __init__(self):

        self.startPose: Pose = defaultStartPose
        self.commands: list[Command] = []

    # Recompute the entire path given the start pose and list of commands
    # Should be called whenever the path is modified
    def recompute(self):

        currentPose: Pose = self.startPose
        for command in self.commands:
            currentPose = command.compute(currentPose)

    # Draw entire path
    def draw(self, screen: pygame.Surface):

        for command in self.commands:
            command.draw(screen)