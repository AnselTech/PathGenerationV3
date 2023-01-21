

class TimeCommand(CustomCommand):

    commandColors = [[120, 120, 120], [195, 195, 195]]
    id = "time"

    def __init__(self, program, nextCustomCommand = None, time = 1):


        icon = graphics.getImage("Images/Commands/time.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.time = time
        self.slider = CommandSlider(self, 0.01, 4, 0.01, "Time (sec)", 1, dx = -50, color = [180, 180, 180])

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.slider.compute()

    def drawOther(self, screen: pygame.Surface):
        num = str(self.slider.getValue())
        graphics.drawText(screen, graphics.FONT15, num + "s", colors.BLACK, self.x + self.INFO_DX, self.y + Command.COMMAND_HEIGHT/2)
        self.slider.draw(screen)

    def getCode(self) -> str:
        num = int(self.slider.getValue() * 1000)
        return f"pros::delay({num});"
