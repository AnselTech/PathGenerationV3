from AbstractButtons.FlipFlopButton import FlipFlopButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
import Utility, graphics, pygame

# A flip-flop button that enables/disables odom
class OdomButton(FlipFlopButton):
    def __init__(self, program):

        self.program = program

        imageOff = graphics.getImage("Images/Buttons/no_wheel.png", 0.05)
        imageOn = graphics.getImage("Images/Buttons/wheel.png", 0.05)
        imageOffHovered = graphics.getLighterImage(imageOff, 0.8)
        imageOnHovered = graphics.getLighterImage(imageOn, 0.8)

        self.tooltip: Tooltip = Tooltip("Toggle using odom in generated code")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 181)
        super().__init__(position, imageOff, imageOffHovered, imageOn, imageOnHovered)


    def isOn(self) -> bool:
        return self.program.state.useOdom

    def toggleButton(self) -> None:
        self.program.state.useOdom = not self.program.state.useOdom
        self.program.recomputeGeneratedCode()

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)