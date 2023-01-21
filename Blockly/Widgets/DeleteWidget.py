from Commands.Widgets.Widget import Widget

class DeleteButton(Clickable, Widget):

    def __init__(self, program, command):

        self.program = program
        self.parent = command

        self.image = graphics.getImage("Images/trash.png", 0.05)
        self.imageH = graphics.getImage("Images/trashH.png", 0.05)

        self.dx = 230
        self.dy = Command.COMMAND_HEIGHT / 2

        super().__init__()

    def computePosition(self, x, y):
        self.x = x + self.dx
        self.y = y + self.dy

    def click(self):
        self.program.deleteCommand(self.parent)

    def checkIfHovering(self, userInput: UserInput) -> bool:
        return Utility.distanceTuples(userInput.mousePosition.screenRef, (self.x, self.y)) < 20

    def draw(self, screen: pygame.Surface):
        image = self.imageH if self.isHovering else self.image
        graphics.drawSurface(screen, image, self.x, self.y)
