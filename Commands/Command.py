from abc import ABC, abstractmethod
from Sliders.Slider import Slider
import pygame, graphics, colors
from MouseInterfaces.Hoverable import Hoverable
from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.TooltipOwner import TooltipOwner
from VisibleElements.Tooltip import Tooltip
from SingletonState.UserInput import UserInput
from SingletonState.SoftwareState import Mode
from SingletonState.ReferenceFrame import Ref
from AbstractButtons.ToggleButton import ToggleButton
from AbstractButtons.ClickButton import ClickButton
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from Simulation.PID import PID
from typing import Iterable
import Utility, texteditor

class CommandAddon:
    pass

class CommandSlider(Slider, CommandAddon):
    def __init__(self, parent, min: float, max: float, step: float, text: str, default: float = 0, dy = 0, dx = 0, program = None, color = None):
        
        self.min = min
        self.max = max
        self.step = step
        self.text = text
        self.default = default
        self.dy = dy
        self.dx = dx

        self.parent: 'Command' = parent
        if program is not None:
            self.program = program
        else:
            self.program = self.parent.program

        width = 65
        if color is None:
            color = self.parent.colors[0]
        super().__init__(self.getX(), self.getY(), width, self.min, self.max, self.step, color, self.text, self.default, textX = width/2, textY = -20, onSet = parent.onSliderUpdate)

    # enter value manually on console
    def onRightClick(self, userInput: UserInput):
        value = input(f"Enter value from {self.min} to {self.max}, or nothing to cancel: ").strip()
        if value != "":
            try:
                self.setValue(float(value))
                print("Value set to:", self.getValue())
            except:
                print("Invalid input.")
        else:
            print("Operation cancelled.")

    def getX(self):
        return self.parent.x + 175 + self.dx

    def getY(self):
        return self.parent.y + self.parent.height / 2 + self.dy

    def compute(self):
        self.x = self.getX()
        self.y = self.getY()
        

class CommandToggle(Clickable, TooltipOwner, CommandAddon):
    def __init__(self, parent: 'Command', options: list[str], text: list[str] = None, width = 35, dx = 0):

        self.parent = parent

        self.options: list[str] = options
        self.tooltips: list[Tooltip] = [Tooltip(optionString) for optionString in self.options]
        self.text: list[str] = text

        self.N = len(self.options)
        self.activeOption: int = 0
        self.hoveringOption: int = -1

        # colors for different states
        self.disabled = (200, 200, 200)
        self.disabledH = (190, 190, 190)
        self.enabled = (180, 180, 180)
        self.enabledH = (170, 170, 170)
        
        self.centerX = 130 + dx
        self.width = width
        self.height = 30

        super().__init__()


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
        if changed:
            self.parent.onToggleClick()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltips[self.tooltipOption].draw(screen, mousePosition)

    def draw(self, screen: pygame.Surface):

        x = self.parent.x + self.centerX - self.width/2
        y = self.parent.y + self.parent.height/2 - self.height/2
        dx = self.width / self.N

        # draw backdrop
        pygame.draw.rect(screen, self.disabled, [x, y, self.width, self.height])

        for i in range(self.N):

            # get color based on whether enabled and/or hovered
            if self.activeOption == i or self.hoveringOption == i:

                if self.activeOption == i:
                    color = self.enabledH if self.hoveringOption == i else self.enabled
                elif self.hoveringOption == i:
                    color = self.disabledH
                # draw filled rect3
                pygame.draw.rect(screen, color, [x, y, dx, self.height])

            if self.text is not None:
                graphics.drawText(screen, graphics.FONT15, self.text[i], colors.BLACK, x + dx/2, y + self.height/2)
            x += dx

            # draw border
            if i != self.N-1:
                graphics.drawThinLine(screen, self.enabledH, x-1, y, x-1, y + self.height)

        # draw border around active option
        x0 = self.parent.x + self.centerX - self.width/2 + dx * self.activeOption
        pygame.draw.rect(screen, [0,0,0], [x0, y, dx + (1 if (self.activeOption == self.N-1) else 0), self.height], 1)


        # kinda bad to do this here, but reset which one was hovered
        self.tooltipOption = self.hoveringOption
        self.hoveringOption = -1


class Command(Hoverable, ABC):

    COMMAND_HEIGHT = 60
    COMMAND_WIDTH = 260

    def __init__(self, parent, colors, toggle: CommandToggle = None, slider: CommandSlider = None, program = None, nextCustomCommand: 'CustomCommand' = None, commented = False):

        super().__init__()

        self.parent = parent
        self.program = parent.program if program is None else program
        self.width = Command.COMMAND_WIDTH
        self.height = Command.COMMAND_HEIGHT
        self.x = 0
        self.y = 0
        self.colors = colors
        self.margin = 2

        self.INFO_DX = self.width * 0.32

        self.toggle: CommandToggle = toggle
        self.slider: CommandSlider = slider

        self.DELTA_SLIDER_Y = 14

        self.nextCustomCommand: 'CustomCommand' = nextCustomCommand
        
        self.commented = commented

    # called by the toggle owned by this command when toggle is toggled
    def onToggleClick(self):
        self.program.recomputeGeneratedCode()

    # called by the slider owned by this command when slider is dragged
    def onSliderUpdate(self):
        self.program.recomputeGeneratedCode()

    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        if self.slider is not None:
            self.slider.compute()

    def checkIfHovering(self, userInput: UserInput) -> bool:
        x,y = userInput.mousePosition.screenRef
        if x < self.x or x > self.x + self.width:
            return False
        if y < self.y or y > self.y + self.height:
            return False
        return True

    def getHoverables(self) -> Iterable[Hoverable]:

        if not self.program.state.mode == Mode.PLAYBACK:
            if self.toggle is not None:
                yield self.toggle

            if self.slider is not None:
                yield self.slider

        yield self

    def isAddOnsHovering(self) -> bool:
        return False

    def isAnyHovering(self) -> bool:
        toggleHovering = self.toggle is not None and self.toggle.isHovering
        sliderHovering = self.slider is not None and self.slider.isHovering
        return self.isAddOnsHovering() or self.isHovering or toggleHovering or sliderHovering or (self.parent is not None and self.parent.isHovering)

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

        if self.commented:
            graphics.drawTransparentRectangle(screen, (255,255,255), 100, self.x, self.y, self.width, self.height)

        

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
        super().__init__(parent, BLUE)

        self.toggle = CommandToggle(self, ["Tuned for precision", "Tuned for speed"], ["Precise", "Fast"], width = 135, dx = 47)

        self.imageLeft = graphics.getImage("Images/Commands/TurnLeft.png", 0.08)
        self.imageRight = graphics.getImage("Images/Commands/TurnRight.png", 0.08)

        

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.direction == 1
        return self.imageRight if clockwise else self.imageLeft

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        y = self.y + self.height/2
        
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y)
    
    def getCode(self) -> str:
        if self.parent.program.state.useOdom:
            nextPoint = self.parent.next.next.position.fieldRef
            return f"turnToPoint(robot, GTU_TURN, {round(nextPoint[0], 2)}, {round(nextPoint[1], 2)});"
        else:
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
        super().__init__(parent, RED)

        toggle = CommandToggle(self, ["Tuned for precision", "Tuned for speed", "No slowdown", "Timed"])
        self.speedSlider = CommandSlider(self, 0, 1, 0.01, "Speed", 1, 0)
        self.timeSlider = CommandSlider(self, 0.1, 5, 0.01, "Time (s)", 1, self.DELTA_SLIDER_Y)

        self.toggle = toggle
        self.isTime: bool = False

        self.imageForward = graphics.getImage("Images/Commands/StraightForward.png", 0.08)
        self.imageReverse = graphics.getImage("Images/Commands/StraightReverse.png", 0.08)
        

    def getHoverables(self) -> Iterable[Hoverable]:

        if not self.program.state.mode == Mode.PLAYBACK:
            yield self.toggle
            yield self.speedSlider
            if self.toggle.get(int) == 3:
                yield self.timeSlider

        yield self

    # called by the toggle owned by this command when toggle is toggled
    def onToggleClick(self):
        super().onToggleClick()
        if self.toggle.get(int) == 3:
            self.slider = self.timeSlider
            self.isTime = True
            self.speedSlider.dy = -self.DELTA_SLIDER_Y
        else:
            self.slider = self.speedSlider
            self.isTime = False
            self.speedSlider.dy = 0
        self._updateSliderPosition()

    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        self._updateSliderPosition()

    def _updateSliderPosition(self):
        self.timeSlider.compute()
        self.speedSlider.compute()

    def getIcon(self) -> pygame.Surface:
        return self.imageForward if self.parent.distance > 0 else self.imageReverse

    def drawInfo(self, screen: pygame.Surface):

        self.speedSlider.draw(screen)
        if self.toggle.get(int) == 3:
            self.timeSlider.draw(screen)

        x = self.x + self.INFO_DX
        dy = 12
        y0 = self.y + self.height/2 - dy
        y1 = self.y + self.height/2 + dy

        string = f"{self.timeSlider.getValue()} s" if self.isTime else self.parent.distanceStr
        graphics.drawText(screen, graphics.FONT15, string, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        
        speed = round(self.speedSlider.getValue(), 2)
        heading = round(self.parent.goalHeading * 180 / 3.1415, 2)
        distance = round(self.parent.distance, 2)

        if self.toggle.get(int) == 3:
            time = self.timeSlider.getValue()
            if distance < 0:
                speed *= -1
            return f"goForwardTimedU(robot, GFU_TURN, {time}, {speed}, getRadians({heading}));"
        elif self.toggle.get(int) == 2:
            if self.program.state.useOdom:
                nextPoint = self.parent.next.position.fieldRef
                return f"goToPoint(robot, NO_SLOWDOWN, GFU_TURN, {round(nextPoint[0], 2)}, {round(nextPoint[1], 2)});"
            else:
                return f"goForwardU(robot, NO_SLOWDOWN({speed}), GFU_TURN, {distance}, getRadians({heading}));"
        else:
            mode = "GFU_DIST_PRECISE" if self.toggle.get(int) == 0 else "GFU_DIST"
            if self.program.state.useOdom:
                nextPoint = self.parent.next.position.fieldRef
                return f"goToPoint(robot, {mode}, GFU_TURN, {round(nextPoint[0], 2)}, {round(nextPoint[1], 2)});"
            else:
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
        super().__init__(parent, GREEN)

        self.imageLeftForward = graphics.getImage("Images/Commands/CurveLeftForward.png", 0.08)
        self.imageRightForward = graphics.getImage("Images/Commands/CurveRightForward.png", 0.08)
        self.imageLeftReverse = graphics.getImage("Images/Commands/CurveLeftReverse.png", 0.08)
        self.imageRightReverse = graphics.getImage("Images/Commands/CurveRightReverse.png", 0.08)

        self.toggle = CommandToggle(self, ["Tuned for precision", "Tuned for speed", "No slowdown"])
        self.slider = CommandSlider(self, 0, 1, 0.01, "Speed", 1)
        

    def getIcon(self) -> pygame.Surface:
        clockwise = self.parent.arc.parity
        if clockwise:
            return self.imageRightReverse if self.parent.reversed else self.imageRightForward
        else:
            return self.imageLeftReverse if self.parent.reversed else self.imageLeftForward

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX
        dy = 12
        y0 = self.y + self.height/2 - dy
        y1 = self.y + self.height/2 + dy

        graphics.drawText(screen, graphics.FONT15, self.parent.goalRadiusStr, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        val = self.toggle.get(int)
        if val == 0:
            mode = "GFU_DIST_PRECISE"
        elif val == 1:
            mode = "GFU_DIST"
        else:
            mode = "NO_SLOWDOWN"

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
        super().__init__(parent, YELLOW)

        self.image = graphics.getImage("Images/Commands/shoot.png", 0.15)

        self.toggle = CommandToggle(self, ["Flywheel", "Cata"])

        self.slider = CommandSlider(self, 2600, 3600, 1, "+/- RPM", 3200, -self.DELTA_SLIDER_Y)

        self.numSlider = CommandSlider(self, 0, 3, 1, "# of disks", 3, self.DELTA_SLIDER_Y)
        

    def getIcon(self) -> pygame.Surface:
        return self.image

    def drawInfo(self, screen: pygame.Surface):
        x = self.x + self.INFO_DX + 5
        y = self.y + self.height/2

        graphics.drawText(screen, graphics.FONT15, "Shoot", colors.BLACK, x, y - 5)

        distance = Utility.distanceTuples(self.parent.parent.position.fieldRef, self.parent.goalPosition)
        graphics.drawText(screen, graphics.FONT15, str(round(distance, 2)), colors.BLACK, x, y + 5)
        self.numSlider.draw(screen)

    def getCode(self) -> str:
        if self.toggle.get(str) == "Cata":
            return "shootCata(robot);"
        else:
            return f"shoot(robot, {self.numSlider.getValue()});"

    def initSimulationController(self, simulationState: SimulationState):
        # temporarily, this controller just does nothing for 20 ticks
        self.idleTicks = 0
        self.maxIdleTicks = 20
        s
    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        self.idleTicks += 1
        return ControllerInputState(0, 0, self.idleTicks >= self.maxIdleTicks)
    
    def isAddOnsHovering(self) -> bool:
        return self.numSlider.isHovering
    
    def getHoverables(self) -> Iterable[Hoverable]:
        yield self.slider
        yield self.numSlider
        yield self.toggle
        yield self
        
    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        self.slider.compute()
        self.numSlider.compute()