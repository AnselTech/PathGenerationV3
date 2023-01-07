from AbstractButtons.FlipFlopButton import FlipFlopButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
import Utility, graphics, pygame

# A flip-flop button that toggles block/text mode
class TextButton(FlipFlopButton):
    def __init__(self, state: SoftwareState):

        self.state: SoftwareState = state

        imageOff = graphics.getImage("Images/Buttons/textoff.png", 0.05)
        imageOn = graphics.getImage("Images/Buttons/texton.png", 0.05)
        imageOffHovered = graphics.getLighterImage(imageOff, 0.8)
        imageOnHovered = graphics.getLighterImage(imageOn, 0.8)

        self.tooltip: Tooltip = Tooltip("Toggle between block commands and c++ code")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 80)
        super().__init__(position, imageOff, imageOffHovered, imageOn, imageOnHovered)


    def isOn(self) -> bool:
        return self.state.isCode

    def toggleButton(self) -> None:
        self.state.isCode = not self.state.isCode

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)