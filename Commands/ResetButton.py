from AbstractButtons.ClickButton import ClickButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
from SingletonState.ReferenceFrame import PointRef, Ref
import Commands.Serializer as Serializer
import Utility, graphics, pygame

# A flip-flop button that toggles block/text mode
class ResetButton(ClickButton):
    def __init__(self, program):

        self.program = program

        imageEnabled = graphics.getImage("Images/Buttons/reset.png", 0.05)
        imageDisabled = graphics.getLighterImage(imageEnabled, 0.4)
        imageHovered = graphics.getLighterImage(imageEnabled, 0.7)

        self.tooltip: Tooltip = Tooltip("Reset to an empty path after saving the current one.")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 217)
        super().__init__(position, imageDisabled, imageEnabled, imageHovered)

    def isDisabled(self) -> bool:
        return False

    def clickEnabledButton(self) -> None:
        self.program.generateSavefile()
        self.program.reset()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)