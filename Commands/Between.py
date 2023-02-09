from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput
from VisibleElements.Tooltip import Tooltip
from MouseInterfaces.TooltipOwner import TooltipOwner
from Commands.Command import Command
from Commands.CustomCommand import *
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

class Plus(Clickable, TooltipOwner):
    
    def __init__(self, between: 'Between', CommandClass, color, text, dx = 0):

        self.between = between
        self.program = self.between.program
        self.x = (self.between.x1 + self.between.x2) / 2 + dx

        self.CommandClass = CommandClass
        
        self.radius = 6
        self.thick = 3 # cross thick radius
        self.thin = 1 # cross thin radius
        
        self.tooltip = Tooltip(text)

        self.color = color

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.between.y)) < 10

    # insert custom command after the previous command
    def click(self) -> None:

        self.between.beforeCommand.nextCustomCommand = self.CommandClass(self.program, self.between.beforeCommand.nextCustomCommand)
        self.program.recomputeCommands()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)

    def draw(self, screen: pygame.Surface):
        graphics.drawCircle(screen, self.x, self.between.y, self.color, self.radius)
        pygame.draw.rect(screen, [255,255,255], [self.x - self.thick, self.between.y - self.thin, self.thick*2, self.thin*2])
        pygame.draw.rect(screen, [255,255,255], [self.x - self.thin, self.between.y - self.thick, self.thin*2, self.thick*2])
        if self.isHovering:
            graphics.drawCircle(screen, self.x, self.between.y, [0,0,0], self.radius+1, width = 1)

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
        classes = [CodeCommand, TimeCommand, IntakeCommand, RollerCommand, DoRollerCommand, FlapCommand]

        m = 20 # distance between plusses
        self.plusses: list[Plus] = []
        dx = -(len(classes)-1) * m / 2
        for c in classes:
            self.plusses.append(Plus(self, c, c.commandColors[0], f"Add {c.text} command...", dx))
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