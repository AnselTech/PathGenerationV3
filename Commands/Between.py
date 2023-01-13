from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput
from VisibleElements.Tooltip import Tooltip
from MouseInterfaces.TooltipOwner import TooltipOwner
from Commands.Command import Command
from Commands.CustomCommand import CustomCommand, CodeCommand, TimeCommand
import Utility, pygame, graphics
from typing import Iterable

"""
A between object is the space between two commands.
When hovered, green bar with a plus sign button (Plus object) appears.
When plus sign button is clicked, ACE command is added
"""

def init():
    global plusImage, plusImageH, tooltip
    plusImage = graphics.getImage("Images/Buttons/plus.png", 0.03)
    plusImageH = graphics.getImage("Images/Buttons/plus2.png", 0.03)
    tooltip = Tooltip("Add a new custom command")

class Plus(Clickable, TooltipOwner):
    
    def __init__(self, between: 'Between', CommandClass, dx = 0):

        self.between = between
        self.program = self.between.beforeCommand.program
        self.x = (self.between.x1 + self.between.x2) / 2 + dx

        self.CommandClass = CommandClass

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.between.y)) < 10

    # insert custom command after the previous command
    def click(self) -> None:

        self.between.beforeCommand.nextCustomCommand = self.CommandClass(self.program, self.between.beforeCommand.nextCustomCommand)
        self.program.recomputeCommands()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        tooltip.draw(screen, mousePosition)

    def draw(self, screen: pygame.Surface):
        
        image = plusImageH if self.isHovering else plusImage
        graphics.drawSurface(screen, image, self.x, self.between.y)


# Object is hidden unless it is hovered.
class Between(Hoverable):

    def __init__(self, beforeCommand: Command, y):
        self.beforeCommand: Command = beforeCommand
        self.program = self.beforeCommand.program
        self.y = y # center y
        
        width = Utility.PANEL_WIDTH * 0.8
        self.x1 = Utility.SCREEN_SIZE + 30 # left x
        self.x2 = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH - 45
        self.thickness = 2

        self.hoverDY = 13
        self.hoverX1 = Utility.SCREEN_SIZE
        self.hoverX2 = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH - 30

        # Initialize list of plus objects which, when clicked, add new commands
        classes: list[CustomCommand] = [CodeCommand, TimeCommand]
        m = 20 # distance between plusses
        self.plusses: list[Plus] = []
        dx = -(len(classes)-1) * m / 2
        for c in classes:
            self.plusses.append(Plus(self, c, dx))
            dx += m

        super().__init__()

    def checkIfHovering(self, userInput: UserInput, margin = None) -> bool:

        if margin is None:
            margin = self.hoverDY

        mx, my = userInput.mousePosition.screenRef
        if mx < self.hoverX1 or mx > self.hoverX2:
            return False
        if my < self.y - margin or my > self.y + margin:
            return False
        return True

    def getHoverables(self) -> Iterable[Hoverable]:
        for plus in self.plusses:
            yield plus
        yield self

    def draw(self, screen: pygame.Surface):
        
        # Only draw when hovered
        if self.isHovering or any(plus.isHovering for plus in self.plusses):
            graphics.drawRoundedLine(screen, [200, 200, 200], self.x1, self.y, self.x2, self.y, self.thickness)
            for plus in self.plusses:
                plus.draw(screen)
        elif self is self.program.hoveredBetween:
            graphics.drawRoundedLine(screen, [100, 230, 100], self.x1, self.y, self.x2, self.y, self.thickness)
            h = 50
            pygame.draw.rect(screen, [255,255,255], [self.beforeCommand.x, self.y - h/2, Command.COMMAND_WIDTH, h], 2)