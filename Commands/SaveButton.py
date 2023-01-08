from AbstractButtons.ClickButton import ClickButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
from SingletonState.ReferenceFrame import PointRef, Ref
import Commands.Serializer as Serializer
import Utility, graphics, pygame, pickle

# A flip-flop button that toggles block/text mode
class SaveButton(ClickButton):
    def __init__(self, program):

        self.program = program

        imageEnabled = graphics.getImage("Images/Buttons/save.png", 0.05)
        imageDisabled = graphics.getLighterImage(imageEnabled, 0.4)
        imageHovered = graphics.getLighterImage(imageEnabled, 0.7)

        self.tooltip: Tooltip = Tooltip("Save the path as a .pg3 file. You can load a", "file by dragging it within the window.")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 140)
        super().__init__(position, imageDisabled, imageEnabled, imageHovered)

    def isDisabled(self) -> bool:
        return self.program.first.next is None

    def clickEnabledButton(self) -> None:
        state = Serializer.State(self.program.first)
        with open("save.pg3", "wb") as file:
            pickle.dump(state, file)
        print("Saved as save.pg3!")

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)