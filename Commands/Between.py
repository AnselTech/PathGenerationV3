from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput
from VisibleElements.Tooltip import Tooltip
from MouseInterfaces.TooltipOwner import TooltipOwner
from Commands.Command import Command, CustomCommand
import Utility, pygame, graphics

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
    
    def __init__(self, between: 'Between'):

        self.between = between
        self.program = self.between.beforeCommand.program
        self.x = (self.between.x1 + self.between.x2) / 2

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.between.y)) < 10

    def click(self) -> None:
        self.between.beforeCommand.nextCustomCommand = CustomCommand(self.program)
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
        self.y = y # center y
        
        width = Utility.PANEL_WIDTH * 0.8
        self.x1 = Utility.SCREEN_SIZE + 30 # left x
        self.x2 = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH - 45
        self.thickness = 2

        self.hoverDY = 13
        self.hoverX1 = Utility.SCREEN_SIZE
        self.hoverX2 = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH - 30

        self.plus: Plus = Plus(self)

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        mx, my = userInput.mousePosition.screenRef
        if mx < self.hoverX1 or mx > self.hoverX2:
            return False
        if my < self.y - self.hoverDY or my > self.y + self.hoverDY:
            return False
        return True

    def draw(self, screen: pygame.Surface):
        
        # Only draw when hovered
        if self.isHovering or self.plus.isHovering:
            graphics.drawRoundedLine(screen, [200, 200, 200], self.x1, self.y, self.x2, self.y, self.thickness)
            self.plus.draw(screen)