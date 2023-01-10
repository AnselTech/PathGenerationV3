from abc import ABC, abstractmethod
from Sliders.Slider import Slider
import pygame, graphics, colors
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.TooltipOwner import TooltipOwner
from VisibleElements.Tooltip import Tooltip
from SingletonState.UserInput import UserInput
from SingletonState.SoftwareState import Mode
from SingletonState.ReferenceFrame import Ref
from AbstractButtons.ToggleButton import ToggleButton
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from Simulation.PID import PID
from typing import Iterable
import Utility

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

    def init(self, parent: 'Command', onSet = None):
        self.parent: 'Command' = parent
        width = 65
        super().__init__(self.getX(), self.getY(), width, self.min, self.max, self.step, self.parent.colors[0], self.text, self.default, textX = width/2, textY = -20, onSet = onSet)


class ToggleOption(Clickable):

    def __init__(self, width: int, height: int, text: str, isTop: bool, onSet = None):

        super().__init__()

        self.onSet = onSet

        self.width = width
        self.height = height
        self.text = text

        self.light = [200, 200, 200]
        self.lightH = [190, 190, 190]
        self.dark = [160, 160, 160]
        self.darkH = [150, 150, 150]
        self.isTop = isTop

    def init(self, toggle: 'CommandToggle', parent: 'Command', onSet = None):
        self.toggle = toggle
        self.parent: 'Command' = parent
        self.onSet = onSet

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
        if self.onSet is not None:
            self.onSet()

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


class CommandToggle(Clickable, TooltipOwner):
    def __init__(self, options: list[str]):

        self.options: list[str] = options
        self.tooltips: list[Tooltip] = [Tooltip(optionString) for optionString in self.options]

        self.N = len(self.options)
        self.activeOption: int = 0
        self.hoveringOption: int = -1

        # colors for different states
        self.disabled = (200, 200, 200)
        self.disabledH = (190, 190, 190)
        self.enabled = (160, 160, 160)
        self.enabledH = (150, 150, 150)
        
        self.centerX = 130
        self.width = 35
        self.height = 30

        super().__init__()
        
    def init(self, parent: 'Command', onSet = None):
        self.parent = parent
        self.onSet = onSet

    # return active option as int/string
    def get(self, datatype) -> str:
        if datatype == str:
            return self.options[self.activeOption]
        elif datatype == int:
            return self.activeOption
        raise Exception("Invalid datatype")

    def checkIfHovering(self, userInput: UserInput) -> bool:
        mx, my = userInput.mousePosition.screenRef

        leftX = self.parent.x + self.centerX - self.width/2
        rightX = leftX + self.width
        if mx < leftX or mx > rightX:
            return False

        topY = self.parent.y + self.parent.height/2 - self.height/2
        bottomY = topY + self.height
        if my < topY or my > bottomY:
            return False

        # at this point, something is definitely being hovered. just need to figure out what
        ratio = (mx - leftX) / self.width # ratio from 0-1
        self.hoveringOption = Utility.clamp(int(ratio * self.N), 0, self.N-1)
        return True

    def click(self):

        if self.hoveringOption == -1:
            raise Exception("clicked but not hovered, error")

        changed: bool = self.activeOption != self.hoveringOption
        self.activeOption = self.hoveringOption
        if changed and self.onSet is not None:
            self.onSet()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltips[self.tooltipOption].draw(screen, mousePosition)

    def draw(self, screen: pygame.Surface):

        x = self.parent.x + self.centerX - self.width/2
        y = self.parent.y + self.parent.height/2 - self.height/2
        dx = self.width / self.N

        # draw backdrop
        pygame.draw.rect(screen, self.disabled, [x, y, self.width, self.height])

        # draw left border
        graphics.drawThinLine(screen, self.enabledH, x-1, y, x-1, y + self.height)

        for i in range(self.N):

            # get color based on whether enabled and/or hovered
            if self.activeOption == i or self.hoveringOption == i:

                if self.activeOption == i:
                    color = self.enabledH if self.hoveringOption == i else self.enabled
                elif self.hoveringOption == i:
                    color = self.disabledH
                # draw filled rect3
                pygame.draw.rect(screen, color, [x, y, dx, self.height])

            x += dx

            # draw border
            graphics.drawThinLine(screen, self.enabledH, x-1, y, x-1, y + self.height)

        # kinda bad to do this here, but reset which one was hovered
        self.tooltipOption = self.hoveringOption
        self.hoveringOption = -1


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
            self.toggle.init(self, self.parent.program.recomputeGeneratedCode)

        self.slider: CommandSlider = slider
        if self.slider is not None:
            self.slider.init(self, self.parent.program.recomputeGeneratedCode)

    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        if self.slider is not None:
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

        if not self.parent.program.state.mode == Mode.PLAYBACK:
            if self.toggle is not None:
                yield self.toggle

            if self.slider is not None:
                yield self.slider

        yield self

    def isAnyHovering(self) -> bool:
        toggleHovering = self.toggle is not None and self.toggle.isHovering
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
            self.toggle.draw(screen)

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

    # subclasses can initialize anything needed before running simulation
    def initSimulationController(self, simulationState: SimulationState):
        pass

    # Run a single tick of the simulation. Given the simulation state, return what the controller values are
    @abstractmethod
    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        pass

class TurnCommand(Command):
    def __init__(self, parent, isShoot = False):

        self.isShoot = isShoot

        BLUE = [[57, 126, 237], [122, 169, 245]]

        toggle = CommandToggle(["Tuned for precision", "Tuned for speed"])

        self.imageLeft = graphics.getImage("Images/Commands/TurnLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/TurnRight.png", 0.08)

        super().__init__(parent, BLUE, toggle = toggle)

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.direction == 1
        return self.imageRight if clockwise else self.imageLeft

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        y = self.y + self.height/2
        
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y)
    
    def getCode(self) -> str:
        mode = "GTU_TURN_PRECISE" if self.toggle.get(int) == 0 else "GTU_TURN"
        num = round(self.parent.goalHeading * 180 / 3.1415, 2)
        return f"goTurnU(robot, {mode}, getRadians({num}));"

    def initSimulationController(self, simulationState: SimulationState):
        tolerance = 5 # tolerance interval in degrees
        self.pid = PID(12, 0, 0.2, tolerance = tolerance * 3.1415 / 180)

    # make a PID turn
    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        error = Utility.deltaInHeading(self.parent.goalHeading, simulationState.robotHeading)
        turnVelocity = self.pid.tick(error)
        return ControllerInputState(turnVelocity, -turnVelocity, self.pid.isDone())


class StraightCommand(Command):
    def __init__(self, parent):

        RED = [[245, 73, 73], [237, 119, 119]]

        toggle = CommandToggle(["Tuned for precision", "Tuned for speed", "No slowdown", "Timed"])
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
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        mode = "GFU_DIST_PRECISE" if self.toggle.get(int) == 0 else "GFU_DIST"
        speed = round(self.slider.getValue(), 2)
        distance = round(self.parent.distance, 2)
        heading = round(self.parent.goalHeading * 180 / 3.1415, 2)
        return f"goForwardU(robot, {mode}({speed}), GFU_TURN, {distance}, getRadians({heading}));"

    def initSimulationController(self, simulationState: SimulationState):
        minSpeed = Simulator.MAX_VELOCITY * 0.05
        self.distancePID = PID(4, 0, 0.2, min = minSpeed, tolerance = 0.3, toleranceRepeated = 3)
        self.turnPID = PID(0.1, 0, 0)
        self.startPosition = simulationState.robotPosition

    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        currentDistance = (simulationState.robotPosition - self.startPosition).magnitude(Ref.FIELD)
        currentDistance *= -1 if self.parent.reversed else 1
        velocity = self.distancePID.tick(self.parent.distance - currentDistance)

        headingError = Utility.deltaInHeading(self.parent.goalHeading, simulationState.robotHeading)
        deltaVelocity = self.turnPID.tick(headingError)
        
        left = velocity + deltaVelocity
        right = velocity - deltaVelocity
        return ControllerInputState(left, right, self.distancePID.isDone())

class CurveCommand(Command):
    def __init__(self, parent):

        GREEN = [[80, 217, 87], [149, 230, 153]]

        self.imageLeft = graphics.getImage("Images/Commands/CurveLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/CurveRight.png", 0.08)

        toggle = CommandToggle(["Tuned for precision", "Tuned for speed"])
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

        graphics.drawText(screen, graphics.FONT15, self.parent.goalRadiusStr, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        mode = "GFU_DIST_PRECISE" if self.toggle.get(int) == 0 else "GFU_DIST"
        speed = round(self.slider.getValue(), 2)
        r = round(self.parent.goalRadius, 2)
        deg1 = round(self.parent.goalBeforeHeading * 180 / 3.1415, 2)
        deg2 = round(self.parent.goalHeading * 180 / 3.1415, 2)
        return f"goCurveU(robot, {mode}({speed}), GCU_CURVE, getRadians({deg1}), getRadians({deg2}), {r});"

    def initSimulationController(self, simulationState: SimulationState):
        # temporarily, this controller just does nothing for 20 ticks
        self.idleTicks = 0
        self.maxIdleTicks = 20

    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        self.idleTicks += 1
        return ControllerInputState(0, 0, self.idleTicks >= self.maxIdleTicks)

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
        return f"shoot(robot);"

    def initSimulationController(self, simulationState: SimulationState):
        # temporarily, this controller just does nothing for 20 ticks
        self.idleTicks = 0
        self.maxIdleTicks = 20

    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        self.idleTicks += 1
        return ControllerInputState(0, 0, self.idleTicks >= self.maxIdleTicks)