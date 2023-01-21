from Blockly.Widgets.SliderWidget import SliderWidget
from Blockly.Commands.Command import Command
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
import graphics, pygame, colors

class ShootCommand(Command):
    def __init__(self, parent):

        YELLOW = [[255, 235, 41], [240, 232, 145]]
        super().__init__(parent, YELLOW)

        self.image = graphics.getImage("Images/Commands/shoot.png", 0.15)
        self.slider = SliderWidget(self, 1500, 4400, 1, "Speed (rpm)", 3300)

        self.widgets.append(self.slider)
        

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

    def _serialize(self, info: dict) -> None:
        info["slider"] = self.slider.getValue()

    # Given serialized data, update object with stored state
    def _deserialize(self, info: dict):
        self.slider.setValue(info["slider"])
