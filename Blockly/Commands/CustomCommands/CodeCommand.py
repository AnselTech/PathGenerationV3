class CodeCommand(CustomCommand):

    commandColors = [[181, 51, 255], [209, 160, 238]]
    id = "code"

    def __init__(self, program, nextCustomCommand = None, text = "// [insert code here]"):

        icon = graphics.getImage("Images/Commands/Custom.png", 0.08)
        super().__init__(self.commandColors, program, icon, nextCustomCommand)

        self.textbox: Textbox = Textbox(self, text)

    def updatePosition(self, x, y):
        super().updatePosition(x,y)
        self.textbox.computePosition(x, y)

    def getOtherHoverables(self) -> Iterable[Hoverable]:
        yield self.textbox

    def drawOther(self, screen: pygame.Surface):
        self.textbox.draw(screen)

    def getCode(self) -> str:
        return "\n" + self.textbox.code + "\n"

    def isAddOnsHovering(self) -> bool:
        return super().isAddOnsHovering() or self.textbox.isHovering