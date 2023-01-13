from MouseInterfaces.Draggable import Draggable
from SingletonState.UserInput import UserInput
import Utility, pygame, graphics, colors

# vertical slider for scroll
class Scroller(Draggable):

    def __init__(self, program, x, y, width, height):

        super().__init__()

        self.program = program

        self.x = x
        self.y = y
        self.width = width
        self.displayHeight = height

        self.contentY = 0
        self.barY = 0

        self.update(0)

    def update(self, contentHeight):
        self.contentHeight = contentHeight

        if contentHeight == 0:
            ratio = 1
        else:
            ratio = min(1, self.displayHeight / contentHeight)
        self.barHeight = self.displayHeight * ratio
        
    def checkIfHovering(self, userInput: UserInput) -> bool:
        mx, my = userInput.mousePosition.screenRef
        if mx < self.x or mx > self.x + self.width:
            return False
        if my < self.y + self.barY or my > self.y + self.barY + self.barHeight:
            return False
        return True

    def startDragging(self, userInput: UserInput):
        self.mouseStartY = userInput.mousePosition.screenRef[1]
        self.startBarY = self.barY

    def beDraggedByMouse(self, userInput: UserInput):
        self.barY = self.startBarY + userInput.mousePosition.screenRef[1] - self.mouseStartY
        self._update()

    def move(self, amount: int):
        self.barY += amount
        self._update()

    def _update(self):
            self.barY = Utility.clamp(self.barY, 0, self.displayHeight - self.barHeight)
            if self.displayHeight == self.barHeight:
                self.barY = 0
            else:
                self.contentY = (self.barY / (self.displayHeight - self.barHeight)) * (self.contentHeight - self.displayHeight)
            self.program.recomputeCommands()

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, colors.BLACK, [self.x, self.y, self.width, self.displayHeight], 1)
        
        color = [200,200,200] if self.isHovering else [220,220,220]
        pygame.draw.rect(screen, color, [self.x + 1, self.y + self.barY + 1, self.width - 2, self.barHeight - 2])