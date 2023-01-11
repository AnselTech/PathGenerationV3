from AbstractButtons.ClickButton import ClickButton
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput
import Utility, pygame, graphics

"""
A between object is the space between two commands.
When hovered, green bar with a plus sign button (Plus object) appears.
When plus sign button is clicked, ACE command is added
"""

def init():
    global plusImage, plusImageBig
    plusImage = graphics.getImage("Images/Buttons/plus.png", 0.1)
    plusImageBig = graphics.getImage("Images/Buttons/plus.png", 0.15)

class Plus(ClickButton):
    
    def __init__(self, between: 'Between'):

        self.between = between
        self.image = plusImage
        self.imageBig = plusImageBig
        self.x = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH / 2

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.between.y)) < 10

    def draw(self, screen: pygame.Surface):
        # draw only when between is visible
        if self.isHovering or self.between.isHovering:
            image = self.imageBig if self.isHovering else self.image
            graphics.drawSurface(screen, image, self.x, self.between.y)


# Object is hidden unless it is hovered.
class Between(Hoverable):

    def __init__(self, y):
        self.y = y # center y
        
        width = Utility.PANEL_WIDTH * 0.8
        self.x1 = Utility.SCREEN_SIZE + Utility.PANEL_WIDTH/2 - width/2 # left x
        self.x2 = self.x1 + width
        self.thickness = 3

        self.hoverDY = 4

        self.plus: Plus = Plus(self)

        super().__init__()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        mx, my = userInput.mousePosition.screenRef
        if not userInput.isMouseOnField:
            return False
        if my < self.y - self.hoverDY or my > self.y + self.hoverDY:
            return False
        return True

    def draw(self, screen: pygame.Surface):
        
        # Only draw when hovered
        if self.isHovering or self.plus.isHovering:
            graphics.drawRoundedLine(screen, [250, 250, 250], self.x1, self.y, self.x2, self.y, self.thickness)