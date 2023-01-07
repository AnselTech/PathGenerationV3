from abc import ABC, abstractmethod
from Sliders.Slider import Slider
import pygame, graphics, colors
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Clickable import Clickable
from SingletonState.UserInput import UserInput
from AbstractButtons.ToggleButton import ToggleButton
from typing import Iterable

class CommandSlider(Slider):
    def __init__(self, min: float, max: float, step: float, text: str, default: float = 0):
        self.min = min
        self.max = max
        self.step = step
        self.text = text
        self.default = default

    def getX(self):
        return self.parent.x + 175

    def getY(self):
        return self.parent.y + self.parent.height / 2 + 7

    def init(self, parent: 'Command'):
        self.parent: 'Command' = parent
        width = 65
        super().__init__(self.getX(), self.getY(), width, self.min, self.max, self.step, self.parent.colors[0], self.text, self.default, textX = width/2, textY = -20)


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
        return self.parent.x + 104

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


    def __init__(self, parent, colors, toggle: CommandToggle = None, slider: CommandSlider = None):

        super().__init__()

        self.parent = parent
        self.width = 260
        self.height = 60
        self.x = 0
        self.y = 0
        self.colors = colors
        self.margin = 2

        self.INFO_DX = self.width * 0.30

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

    def isAnyHovering(self) -> bool:
        toggleHovering = self.toggle is not None and (self.toggle.top.isHovering or self.toggle.bottom.isHovering)
        sliderHovering = self.slider is not None and self.slider.isHovering
        return self.isHovering or toggleHovering or sliderHovering or self.parent.isHovering

    def draw(self, screen: pygame.Surface):

        if self.isAnyHovering():
            # border
            pygame.draw.rect(screen, self.colors[0], [self.x - self.margin, self.y - self.margin, self.width + self.margin*2, self.height + self.margin*2])

        # parameters
        pygame.draw.rect(screen, self.colors[1], [self.x, self.y, self.width, self.height])

        # icon
        width = self.height * 0.9
        pygame.draw.rect(screen, self.colors[0], [self.x, self.y, width, self.height])
        graphics.drawSurface(screen, self.getIcon(), self.x + width/2, self.y + self.height/2)

        # command info
        self.drawInfo(screen)

        # toggle
        if self.toggle is not None:
            self.toggle.bottom.draw(screen)
            self.toggle.top.draw(screen)

        # Slider
        if self.slider is not None:
            self.slider.draw(screen)

        

    @abstractmethod
    def getIcon(self) -> pygame.Surface:
        pass

    # override with subclasses
    def drawInfo(self, screen: pygame.Surface):
        pass

    @abstractmethod
    def getCode(self) -> str:
        pass

class TurnCommand(Command):
    def __init__(self, parent, isShoot = False):

        self.isShoot = isShoot

        BLUE = [[57, 126, 237], [122, 169, 245]]

        toggle = CommandToggle("PREC", "FAST")
        slider = CommandSlider(0, 1, 0.01, "Speed", 1)

        self.imageLeft = graphics.getImage("Images/Commands/TurnLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/TurnRight.png", 0.08)

        super().__init__(parent, BLUE, toggle = toggle, slider = slider)

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.direction == 1
        return self.imageRight if clockwise else self.imageLeft

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        y = self.y + self.height/2

        text = self.parent.headingStr if self.isShoot else self.parent.next.beforeHeadingStr
        graphics.drawText(screen, graphics.FONT15, text, colors.BLACK, x, y)
    
    def getCode(self) -> str:
        mode = "GTU_TURN_PRECISE" if self.toggle.isTopActive else "GTU_TURN"
        deg = round(self.parent.goalHeading * 180 / 3.1415, 1)
        return f"goTurnU(robot, {mode}, getRadians({deg}));"


class StraightCommand(Command):
    def __init__(self, parent):

        RED = [[245, 73, 73], [237, 119, 119]]

        toggle = CommandToggle("PREC", "FAST")
        slider = CommandSlider(0, 1, 0.01, "Speed", 1)

        self.image = graphics.getImage("Images/Commands/Straight.png", 0.08)

        super().__init__(parent, RED, toggle = toggle, slider = slider)

    def getIcon(self) -> pygame.Surface:
        return self.image

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        dy = 12
        y0 = self.y + self.height/2 - dy
        y1 = self.y + self.height/2 + dy

        graphics.drawText(screen, graphics.FONT15, self.parent.distanceStr, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.beforeHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        mode = "GFU_DIST_PRECISE" if self.toggle.isTopActive else "GFU_DIST"
        dist = round(self.parent.distance, 1)
        deg = round(self.parent.beforeHeading * 180 / 3.1415, 1)
        return f"goForwardU(robot, {mode}, GFU_TURN, {dist}, getRadians({deg}));"

class CurveCommand(Command):
    def __init__(self, parent):

        GREEN = [[80, 217, 87], [149, 230, 153]]

        self.imageLeft = graphics.getImage("Images/Commands/CurveLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/CurveRight.png", 0.08)

        toggle = CommandToggle("PREC", "FAST")
        slider = CommandSlider(0, 1, 0.01, "Speed", 1)
        super().__init__(parent, GREEN, toggle = toggle, slider = slider)

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.arc.parity
        return self.imageRight if clockwise else self.imageLeft

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        dy = 12
        y0 = self.y + self.height/2 - dy
        y1 = self.y + self.height/2 + dy

        graphics.drawText(screen, graphics.FONT15, self.parent.arcLengthStr, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.afterHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        mode = "GFU_DIST_PRECISE" if self.toggle.isTopActive else "GFU_DIST"
        dist = round(self.parent.arcLength, 1)
        deg1 = round(self.parent.beforeHeading * 180 / 3.1415, 1)
        deg2 = round(self.parent.afterHeading * 180 / 3.1415, 1)
        return f"goCurveU(robot, {mode}, GCU_CURVE, {dist}, getRadians({deg1}), getRadians({deg2}));"

class ShootCommand(Command):
    def __init__(self, parent):

        YELLOW = [[255, 235, 41], [240, 232, 145]]

        self.image = graphics.getImage("Images/Commands/shoot.png", 0.15)

        slider = CommandSlider(1500, 3600, 1, "Speed (rpm)", 3300)
        super().__init__(parent, YELLOW, slider = slider)

    def getIcon(self) -> pygame.Surface:
        return self.image

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX + 5
        y = self.y + self.height/2

        graphics.drawText(screen, graphics.FONT20, "Shoot", colors.BLACK, x, y)

    def getCode(self) -> str:
        return f"shoot();"
