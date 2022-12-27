from abc import ABC, abstractmethod
from Sliders.Slider import Slider
import pygame, graphics
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Clickable import Clickable
from SingletonState.UserInput import UserInput
from AbstractButtons.ToggleButton import ToggleButton
from typing import Iterable

class CommandSlider(Slider):
    def __init__(self, min: float, max: float, step: float, text: str):
        self.min = min
        self.max = max
        self.step = step
        self.text = text

    def getX(self):
        return self.parent.x + 200

    def getY(self):
        return self.parent.y + self.parent.height / 2 + 7

    def init(self, parent: 'Command'):
        self.parent: 'Command' = parent
        width = 50
        super().__init__(self.getX(), self.getY(), width, self.min, self.max, self.step, self.parent.colors[0], self.text, textX = width/2, textY = -20)


class ToggleOption(Clickable):

    def __init__(self, width: int, height: int, text: str, isTop: bool):

        super().__init__()

        self.width = width
        self.height = height
        self.text = text

        self.light = [200, 200, 200]
        self.lightH = [190, 190, 190]
        self.dark = [160, 160, 160]
        self.darkH = [150, 150, 150]
        self.isTop = isTop

    def init(self, toggle: 'CommandToggle', parent: 'Command'):
        self.toggle = toggle
        self.parent: 'Command' = parent

    def getX(self):
        return self.parent.x + 124

    def getY(self):
        return self.parent.y + 10 + (0 if self.isTop else self.height)

    def checkIfHovering(self, userInput: UserInput) -> bool:
        x = self.getX()
        y = self.getY()
        mx, my = userInput.mousePosition.screenRef
        if mx < x or mx > x + self.width:
            return False
        if my < y or my > y + self.height:
            return False
        return True

    def click(self):
        self.toggle.isTopActive = self.isTop

    def draw(self, screen: pygame.Surface):

        x = self.getX()
        y = self.getY()

        # Draw the box
        if self.toggle.isTopActive == self.isTop:
            color = self.darkH if self.isHovering else self.dark
        else:
            color = self.lightH if self.isHovering else self.light
        pygame.draw.rect(screen, color, [x, y, self.width, self.height])

        # draw black border
        if self.toggle.isTopActive == self.isTop:
            pygame.draw.rect(screen, [0,0,0], [x, y, self.width, self.height], 1)

        # Draw text
        graphics.drawText(screen, graphics.FONT15, self.text, [0,0,0], x + self.width/2, y + self.height/2)


class CommandToggle:
    def __init__(self, topStr: str, bottomStr: str):

        self.isTopActive = True
        
        w = 50
        h = 20
        self.top = ToggleOption(w, h, topStr, True)
        self.bottom = ToggleOption(w, h, bottomStr, False)
        
    def init(self, parent: 'Command'):
        self.top.init(self, parent)
        self.bottom.init(self, parent)


class Command(Hoverable, ABC):

    def __init__(self, imagePath: str, colors, toggle: CommandToggle = None, slider: CommandSlider = None):

        super().__init__()

        self.width = 270
        self.height = 60
        self.x = 0
        self.y = 0
        self.colors = colors
        self.margin = 2

        self.image = graphics.getImage(imagePath, 0.08)

        self.toggle: CommandToggle = toggle
        if self.toggle is not None:
            self.toggle.init(self)

        self.slider: CommandSlider = slider
        if self.slider is not None:
            self.slider.init(self)

    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        self.slider.x = self.slider.getX()
        self.slider.y = self.slider.getY()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        x,y = userInput.mousePosition.screenRef
        if x < self.x or x > self.x + self.width:
            return False
        if y < self.y or y > self.y + self.height:
            return False
        return True

    def getHoverables(self) -> Iterable[Hoverable]:

        if self.toggle is not None:
            yield self.toggle.top
            yield self.toggle.bottom

        if self.slider is not None:
            yield self.slider

        yield self

    def draw(self, screen: pygame.Surface):
        
        if self.isHovering:
            # border
            pygame.draw.rect(screen, self.colors[0], [self.x - self.margin, self.y - self.margin, self.width + self.margin*2, self.height + self.margin*2])

        # parameters
        pygame.draw.rect(screen, self.colors[2], [self.x, self.y, self.width, self.height])

        # icon
        width = self.height * 0.9
        pygame.draw.rect(screen, self.colors[0], [self.x, self.y, width, self.height])
        graphics.drawSurface(screen, self.image, self.x + width/2, self.y + self.height/2)

        # toggle
        if self.toggle is not None:
            self.toggle.bottom.draw(screen)
            self.toggle.top.draw(screen)

        # Slider
        if self.slider is not None:
            self.slider.draw(screen)

class TurnCommand(Command):
    pass

class ForwardCommand(Command):
    def __init__(self):

        RED = [[245, 73, 73], [240, 91, 91], [237, 119, 119]]

        toggle = CommandToggle("PREC", "FAST")
        slider = CommandSlider(0, 1, 0.01, "Speed")
        super().__init__("Images/Commands/Straight.png", RED, toggle, slider)

class CurveCommand(Command):
    pass

class ShootCommand(Command):
    pass