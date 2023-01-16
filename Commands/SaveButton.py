from AbstractButtons.ClickButton import ClickButton
from SingletonState.SoftwareState import SoftwareState
from VisibleElements.Tooltip import Tooltip
from SingletonState.ReferenceFrame import PointRef, Ref
import Commands.Serializer as Serializer
import Utility, graphics, pygame, pickle
import os.path, os

# A flip-flop button that toggles block/text mode
class SaveButton(ClickButton):
    def __init__(self, program):

        self.program = program

        imageEnabled = graphics.getImage("Images/Buttons/save.png", 0.05)
        imageDisabled = graphics.getLighterImage(imageEnabled, 0.4)
        imageHovered = graphics.getLighterImage(imageEnabled, 0.7)

        self.tooltip: Tooltip = Tooltip("Save the path as a .pg3 file. You can load a", "file by dragging it within the window.")

        position = (Utility.SCREEN_SIZE - 50, Utility.SCREEN_SIZE - 149)
        super().__init__(position, imageDisabled, imageEnabled, imageHovered)

    def isDisabled(self) -> bool:
        return self.program.first.next is None

    def clickEnabledButton(self) -> None:
        state = Serializer.State(self.program.first)

        if not os.path.exists("saves"):
            os.makedirs("saves")

        i = 1
        filename = f"saves/save_{Utility.VERSION_LOWER}.pg3"
        while os.path.isfile(filename):
            i += 1
            filename = f"saves/save{i}_{Utility.VERSION_LOWER}.pg3"

        with open(filename, "wb") as file:
            pickle.dump(state, file)
        print(f"Saved as {filename}!")

    def drawTooltip(self, screen: pygame.Surface, mousePosition: tuple) -> None:
        self.tooltip.draw(screen, mousePosition)