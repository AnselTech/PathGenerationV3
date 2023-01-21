from Blockly.Commands.Command import Command
from Blockly.Widgets.Widget import Widget
from Blockly.Widgets.ToggleWidget import ToggleWidget
from Blockly.Widgets.SliderWidget import SliderWidget
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState
import graphics, pygame, colors

class CurveCommand(Command):
    def __init__(self, parent):

        GREEN = [[80, 217, 87], [149, 230, 153]]
        super().__init__(parent, GREEN)

        self.imageLeftForward = graphics.getImage("Images/Commands/CurveLeftForward.png", 0.08)
        self.imageRightForward = graphics.getImage("Images/Commands/CurveRightForward.png", 0.08)
        self.imageLeftReverse = graphics.getImage("Images/Commands/CurveLeftReverse.png", 0.08)
        self.imageRightReverse = graphics.getImage("Images/Commands/CurveRightReverse.png", 0.08)

        self.toggle = ToggleWidget(self, ["Tuned for precision", "Tuned for speed", "No slowdown"])
        self.slider = SliderWidget(self, 0, 1, 0.01, "Speed", 1)
        
        self.widgets.append(self.toggle)
        self.widgets.append(self.slider)


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

    def _serialize(self, info: dict) -> None:
        info["toggle"] = self.toggle.get(int)
        info["slider"] = self.slider.getValue()

    # Given serialized data, update object with stored state
    def _deserialize(self, info: dict):
        self.toggle.activeOption = info["toggle"]
        self.slider.setValue(info["slider"])