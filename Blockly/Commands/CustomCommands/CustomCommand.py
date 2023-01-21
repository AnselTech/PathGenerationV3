from MouseInterfaces.Draggable import Draggable
from MouseInterfaces.Clickable import Clickable
from MouseInterfaces.Hoverable import Hoverable
from SingletonState.UserInput import UserInput
import graphics, Utility, pygame, colors, texteditor
from typing import Iterable

from Blockly.Commands.Command import Command

from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
from Simulation.Simulator import Simulator
from Simulation.PID import PID


class CustomCommand(Draggable, Command):
    def __init__(self, color, program, icon, nextCustomCommand = None):
        
        Command.__init__(self, None, color, program = program, nextCustomCommand = nextCustomCommand)
        self.icon = icon
        self.delete: DeleteButton = DeleteButton(program, self)

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.delete.computePosition(x, y)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        return
        yield

    def getHoverables(self) -> Iterable[Hoverable]:

        for hoverable in self.getOtherHoverables():
            yield hoverable

        yield self.delete
        yield self

    def getIcon(self) -> pygame.Surface:
        return self.icon

    def drawOther(self, screen: pygame.Surface):
        pass

    def drawInfo(self, screen: pygame.Surface):
        self.delete.draw(screen)
        self.drawOther(screen)

    def initSimulationController(self, simulationState: SimulationState):
        pass

    def simulateTick(self, simulationState: SimulationState) -> ControllerInputState:
        return ControllerInputState(0, 0, True)

    # Callback when the dragged object was just released
    def stopDragging(self):
        self.program.stopDragCustomCommand(self)

    # Called when the object was just pressed at the start of a drag
    def startDragging(self, userInput: UserInput):
        pass
    
    # Called every frame that the object is being dragged. Most likely used to update the position of the object based
    # on where the mouse is
    def beDraggedByMouse(self, userInput: UserInput):
        self.program.dragCustomCommand(userInput)

    def isAddOnsHovering(self) -> bool:
        return self.delete.isHovering