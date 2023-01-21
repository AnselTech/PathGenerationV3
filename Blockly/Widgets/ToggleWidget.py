from Commands.Widgets.Widget import Widget

class ToggleWidget(Clickable, TooltipOwner, Widget):
    def __init__(self, parent: 'Command', options: list[str], text: list[str] = None, width = 35, dx = 0):

        self.parent = parent

        self.options: list[str] = options
        self.tooltips: list[Tooltip] = [Tooltip(optionString) for optionString in self.options]
        self.text: list[str] = text

        self.N = len(self.options)
        self.activeOption: int = 0
        self.hoveringOption: int = -1

        # colors for different states
        self.disabled = (200, 200, 200)
        self.disabledH = (190, 190, 190)
        self.enabled = (180, 180, 180)
        self.enabledH = (170, 170, 170)
        
        self.centerX = 130 + dx
        self.width = width
        self.height = 30

        super().__init__()


    # return active option as int/string
    def get(self, datatype) -> str:
        if datatype == str:
            return self.options[self.activeOption]
        elif datatype == int:
            return self.activeOption
        raise Exception("Invalid datatype")

    def checkIfHovering(self, userInput: UserInput) -> bool:
        mx, my = userInput.mousePosition.screenRef

        leftX = self.parent.x + self.centerX - self.width/2
        rightX = leftX + self.width
        if mx < leftX or mx > rightX:
            return False

        topY = self.parent.y + self.parent.height/2 - self.height/2
        bottomY = topY + self.height
        if my < topY or my > bottomY:
            return False

        # at this point, something is definitely being hovered. just need to figure out what
        ratio = (mx - leftX) / self.width # ratio from 0-1
        self.hoveringOption = Utility.clamp(int(ratio * self.N), 0, self.N-1)
        return True

    def click(self):

        if self.hoveringOption == -1:
            raise Exception("clicked but not hovered, error")

        changed: bool = self.activeOption != self.hoveringOption
        self.activeOption = self.hoveringOption
        if changed:
            self.parent.onToggleClick()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltips[self.tooltipOption].draw(screen, mousePosition)

    def draw(self, screen: pygame.Surface):

        x = self.parent.x + self.centerX - self.width/2
        y = self.parent.y + self.parent.height/2 - self.height/2
        dx = self.width / self.N

        # draw backdrop
        pygame.draw.rect(screen, self.disabled, [x, y, self.width, self.height])

        for i in range(self.N):

            # get color based on whether enabled and/or hovered
            if self.activeOption == i or self.hoveringOption == i:

                if self.activeOption == i:
                    color = self.enabledH if self.hoveringOption == i else self.enabled
                elif self.hoveringOption == i:
                    color = self.disabledH
                # draw filled rect3
                pygame.draw.rect(screen, color, [x, y, dx, self.height])

            if self.text is not None:
                graphics.drawText(screen, graphics.FONT15, self.text[i], colors.BLACK, x + dx/2, y + self.height/2)
            x += dx

            # draw border
            if i != self.N-1:
                graphics.drawThinLine(screen, self.enabledH, x-1, y, x-1, y + self.height)

        # draw border around active option
        x0 = self.parent.x + self.centerX - self.width/2 + dx * self.activeOption
        pygame.draw.rect(screen, [0,0,0], [x0, y, dx + (1 if (self.activeOption == self.N-1) else 0), self.height], 1)


        # kinda bad to do this here, but reset which one was hovered
        self.tooltipOption = self.hoveringOption
        self.hoveringOption = -1