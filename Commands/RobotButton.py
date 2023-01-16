from AbstractButtons.FlipFlopButton import FlipFlopButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
import Utility, graphics, pygame

# A flip-flop button that show/hides robot
class RobotButton(FlipFlopButton):
    def __init__(self, state: SoftwareState):

        self.state: SoftwareState = state

        imageOff = graphics.getImage("Images/Buttons/hide.png", 0.05)
        imageOn = graphics.getImage("Images/Buttons/show.png", 0.05)
        imageOffHovered = graphics.getLighterImage(imageOff, 0.8)
        imageOnHovered = graphics.getLighterImage(imageOn, 0.8)

        self.tooltip: Tooltip = Tooltip("Toggle displaying the robot when drawing the path")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 117)
        super().__init__(position, imageOff, imageOffHovered, imageOn, imageOnHovered)


    def isOn(self) -> bool:
        return self.state.showRobot

    def toggleButton(self) -> None:
        self.state.showRobot = not self.state.showRobot

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)