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

from Blockly.Widgets.Widget import Widget
import Blockly.Commands.CustomCommands.CustomManager as CustomManager


class Command(Hoverable, ABC):

    COMMAND_HEIGHT = 60
    COMMAND_WIDTH = 260

    def __init__(self, program, parent, colors: tuple, nextCustomCommand: 'CustomCommand' = None, commented = False):

        super().__init__()

        self.parent = parent
        self.program = program
        self.width = Command.COMMAND_WIDTH
        self.height = Command.COMMAND_HEIGHT
        self.x = 0
        self.y = 0
        self.colors = colors
        self.margin = 2

        self.widgets: list[Widget] = []

        self.INFO_DX = self.width * 0.32
        self.nextCustomCommand: 'Command' = nextCustomCommand
        
        self.commented: bool = commented

    # called by the toggle owned by this command when toggle is toggled
    def onToggleClick(self):
        self.program.recomputeGeneratedCode()

    # called by the slider owned by this command when slider is dragged
    def onSliderUpdate(self):
        self.program.recomputeGeneratedCode()

    # Called whenever command is moved. Recompute position and position of its widgets
    def updatePosition(self, x, y):
        self.x = x
        self.y = y
        for widget in self.widgets:
            widget.updatePosition(x,y)

    # Check if the command object itself is being hovered by mouse
    def checkIfHovering(self, userInput: UserInput) -> bool:
        x,y = userInput.mousePosition.screenRef
        if x < self.x or x > self.x + self.width:
            return False
        if y < self.y or y > self.y + self.height:
            return False
        return True

    # get all the hoverables, including widgets and command itself
    def getHoverables(self) -> Iterable[Hoverable]:

        for widget in self.widgets:
            if widget.isVisible:
                yield widget

        yield self

    # whether the command or any of widgets are being currently hovered
    def isAnyHovering(self) -> bool:

        for hoverable in self.getHoverables():
            if hoverable.isHovering:
                return True
        return False

    
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

        for widget in self.widgets:
            if widget.isVisible:
                widget.draw(screen)

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

    # optionally override this to add additional serialized data for subclasses to info dictionary
    def _serialize(self, info: dict) -> None:
        pass

    # Return a serialized representation of the object as a dictionary
    def serialize(self) -> dict:

        if self.nextCustomCommand is None:
            custom = None
        else:
            custom = self.nextCustomCommand.serialize()

        info = {
            "commented" : self.commented,
            "custom" : custom
        }

        self._serialize(info)

        return info


    # optionally override this to deserialize additional data for subclasses from info dictionary
    def _deserialize(self, info: dict) -> None:
        pass

    # Given serialized data, update object with stored state
    def deserialize(self, info: dict) -> None:
        if info["custom"] is None:
            self.nextCustomCommand = None
        else:
            self.nextCustomCommand = CustomManager.deserializeCustomCommand(info["custom"])

        self.commented = info["commented"]

        self._deserialize(info)