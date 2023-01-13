from AbstractButtons.ClickButton import ClickButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
import Utility, graphics, pygame

# A flip-flop button that toggles block/text mode
class PrintButton(ClickButton):
    def __init__(self, program):

        self.program = program

        imageEnabled = graphics.getImage("Images/Buttons/print.png", 0.05)
        imageDisabled = graphics.getLighterImage(imageEnabled, 0.4)
        imageHovered = graphics.getLighterImage(imageEnabled, 0.7)

        self.tooltip: Tooltip = Tooltip("Print the generated c++ code into the console")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 110)
        super().__init__(position, imageDisabled, imageEnabled, imageHovered)


    def isDisabled(self) -> bool:
        return self.program.first.next is None

    def clickEnabledButton(self) -> None:
        print(self.program.code)

        with open("Generated_Code.txt", "w") as file:
            for line in self.program.code.split("\n"):
                file.write(line + "\n")

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)