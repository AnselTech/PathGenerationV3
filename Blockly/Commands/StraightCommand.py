from Blockly.Commands.Command import Command
from Blockly.Widgets.ToggleWidget import ToggleWidget
from Blockly.Widgets.SliderWidget import SliderWidget
from Simulation.ControllerInputState import ControllerInputState
from Simulation.SimulationState import SimulationState

from MouseInterfaces.Hoverable import Hoverable

from SingletonState.SoftwareState import Mode, SoftwareState

import graphics, colors, Utility
from typing import Iterable

class StraightCommand(Command):
    def __init__(self, parent):

        RED = [[245, 73, 73], [237, 119, 119]]
        super().__init__(parent, RED)

        self.DELTA_SLIDER_Y = 14

        self.toggle = ToggleWidget(self, ["Tuned for precision", "Tuned for speed", "No slowdown", "Timed"])
        self.speedSlider = SliderWidget(self, 0, 1, 0.01, "Speed", 1, 0)
        self.timeSlider = SliderWidget(self, 0.1, 5, 0.01, "Time (s)", 1, self.DELTA_SLIDER_Y)
        self.widgets.append(self.toggle)
        self.widgets.append(self.speedSlider)
        self.widgets.append(self.timeSlider)

        self.imageForward = graphics.getImage("Images/Commands/StraightForward.png", 0.08)
        self.imageReverse = graphics.getImage("Images/Commands/StraightReverse.png", 0.08)

    def isTimeMode(self) -> bool:
        return self.toggle.get(int) == 3

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

        string = f"{self.timeSlider.getValue()} s" if self.isTimeMode() else self.parent.distanceStr
        graphics.drawText(screen, graphics.FONT15, string, colors.BLACK, x, y0)
        graphics.drawText(screen, graphics.FONT15, self.parent.goalHeadingStr, colors.BLACK, x, y1)

    def getCode(self) -> str:
        
        speed = round(self.speedSlider.getValue(), 2)
        heading = round(self.parent.goalHeading * 180 / 3.1415, 2)
        distance = round(self.parent.distance, 2)

        if self.toggle.get(int) == 3:
            time = self.timeSlider.getValue()
            return f"goForwardTimedU(robot, GFU_TURN, {time}, {speed}, getRadians({heading}));"
        elif self.toggle.get(int) == 2:
            return f"goForwardU(robot, NO_SLOWDOWN({speed}), GFU_TURN, {distance}, getRadians({heading}));"
        else:
            mode = "GFU_DIST_PRECISE" if self.toggle.get(int) == 0 else "GFU_DIST"
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

    def _serialize(self, info: dict) -> None:
        info["toggle"] = self.toggle.get(int)
        info["speed"] = self.speedSlider.getValue()
        info["time"] = self.timeSlider.getValue()

    # Given serialized data, update object with stored state
    def _deserialize(self, info: dict):
        self.toggle.activeOption = info["toggle"]
        self.speedSlider.setValue(info["speed"])
        self.timeSlider.setValue(info["time"])