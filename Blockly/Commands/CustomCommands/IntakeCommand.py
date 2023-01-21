

class IntakeCommand(CustomCommand):

    commandColors = [[248, 128, 34], [251, 172, 110]]
    id = "intake"

    def __init__(self, program, nextCustomCommand = None, intakeSpeed = 1):

        icon = graphics.getImage("Images/Commands/intake.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.slider = CommandSlider(self, -1, 1, 0.05, "Intake speed", intakeSpeed, dx = -50)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.slider

    def drawOther(self, screen: pygame.Surface):
        text = f"{int(round(self.slider.getValue() * 100))}%"
        graphics.drawText(screen, graphics.FONT15, text, colors.BLACK, self.x + self.INFO_DX, self.y + Command.COMMAND_HEIGHT/2)
        self.slider.draw(screen)

    def getCode(self) -> str:
        return f"setEffort(*robot.intake, {round(self.slider.getValue(), 2)});"