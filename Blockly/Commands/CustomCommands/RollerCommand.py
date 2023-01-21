

class RollerCommand(CustomCommand):

    commandColors = [[255, 86, 242], [251, 147, 243]]
    id = "roller"

    def __init__(self, program, nextCustomCommand = None, rollerSpeed = 1, toggleMode = 0, rollerDistance = 180, rollerTime = 0.5):

        icon = graphics.getImage("Images/Commands/roller.png", 0.07)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.toggle = CommandToggle(self, ["Run for distance", "Run for time"], ["D", "T"],  dx = -40)
        self.sliderSpeed = CommandSlider(self, -1, 1, 0.05, "Roller speed", rollerSpeed, dx = -50, dy = -14)
        self.sliderDistance = CommandSlider(self, -360, 360, 10, "Rotations (deg)", rollerDistance, dx = -50, dy = 14)
        self.sliderTime = CommandSlider(self, 0.1, 3, 0.1, "Time (seconds)", rollerTime, dx = -50, dy = 14)

        self.toggle.activeOption = toggleMode

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.toggle
        yield self.sliderSpeed
        if self.toggle.get(int) == 0:
            yield self.sliderDistance
        else:
            yield self.sliderTime

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.sliderSpeed.compute()
        self.sliderDistance.compute()
        self.sliderTime.compute()

    def drawOther(self, screen: pygame.Surface):
        self.sliderSpeed.draw(screen)
        if self.toggle.get(int) == 0:
            self.sliderDistance.draw(screen)
        else:
            self.sliderTime.draw(screen)

    def getCode(self) -> str:
        if self.toggle.get(int) == 0:
            return f"\nmoveRollerDegrees(robot, {self.sliderDistance.getValue()}, {self.sliderSpeed.getValue()});\n"
        else:
            return f"\nmoveRollerTime(robot, {self.sliderTime.getValue()}, {self.sliderSpeed.getValue()});\n"

    def isAddOnsHovering(self) -> bool:
        return super().isAddOnsHovering() or self.sliderSpeed.isHovering or self.sliderTime.isHovering